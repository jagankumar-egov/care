#!/usr/bin/env python
"""
Management command to create MMC Hospital fixtures.
Creates:
- 1 MMC Hospital facility
- 3 Departments: BP (Blood Pressure), Sugar (Diabetes), Ortho (Orthopedics)
- 3 Doctors per department (9 total)
- Availability for each doctor for the current week
"""

import datetime
import secrets
import uuid

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db import transaction
from django.utils import timezone
from faker import Faker

from care.emr.models import FacilityOrganization, Organization
from care.emr.models.organization import FacilityOrganizationUser, OrganizationUser
from care.emr.models.scheduling.schedule import Availability, Schedule, SchedulableResource
from care.emr.resources.facility.spec import FacilityCreateSpec
from care.emr.resources.facility_organization.spec import (
    FacilityOrganizationTypeChoices,
    FacilityOrganizationWriteSpec,
)
from care.emr.resources.organization.spec import OrganizationTypeChoices, OrganizationWriteSpec
from care.emr.resources.patient.spec import GenderChoices
from care.emr.resources.user.spec import UserCreateSpec, UserTypeOptions
from care.security.models import RoleModel
from care.users.models import User


def generate_unique_indian_phone_number():
    return (
        "+91"
        + secrets.choice(["9", "8", "7", "6"])
        + "".join([str(secrets.randbelow(10)) for _ in range(9)])
    )


# Department configurations
DEPARTMENTS = [
    {
        "name": "Blood Pressure Department",
        "short_name": "BP",
        "description": "Department specializing in blood pressure monitoring and hypertension treatment",
    },
    {
        "name": "Diabetes Care Department",
        "short_name": "Sugar",
        "description": "Department specializing in diabetes management and sugar level monitoring",
    },
    {
        "name": "Orthopedics Department",
        "short_name": "Ortho",
        "description": "Department specializing in bone, joint, and musculoskeletal care",
    },
]

# Doctor names for each department
DOCTOR_NAMES = {
    "BP": [
        {"first_name": "Rajesh", "last_name": "Kumar"},
        {"first_name": "Priya", "last_name": "Sharma"},
        {"first_name": "Amit", "last_name": "Patel"},
    ],
    "Sugar": [
        {"first_name": "Sneha", "last_name": "Reddy"},
        {"first_name": "Vikram", "last_name": "Singh"},
        {"first_name": "Anjali", "last_name": "Nair"},
    ],
    "Ortho": [
        {"first_name": "Suresh", "last_name": "Menon"},
        {"first_name": "Kavitha", "last_name": "Rao"},
        {"first_name": "Arjun", "last_name": "Verma"},
    ],
}


class Command(BaseCommand):
    help = "Generate MMC Hospital fixtures with departments, doctors, and availability"

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            type=str,
            default="Doctor@123",
            help="Default password for all doctor accounts",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write(
                self.style.ERROR(
                    "This command should not be run in production. Exiting..."
                )
            )
            return

        self.stdout.write("Starting MMC Hospital fixtures generation...")

        # Ensure permissions and valuesets are synced
        self.stdout.write("Syncing permissions and valuesets...")
        call_command("sync_permissions_roles")
        call_command("sync_valueset")

        try:
            with transaction.atomic():
                self._generate_fixtures(options)
                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully generated MMC Hospital fixtures!"
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Transaction rolled back due to error: {e}")
            )
            raise

    def _generate_fixtures(self, options):
        """Generate all the fixture data within a transaction context."""
        fake = Faker("en_IN")
        self.fake = fake
        default_password = options["password"]

        # Get or create admin user
        super_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "user_type": "admin",
                "is_superuser": True,
                "is_staff": True,
                "first_name": "Admin",
                "last_name": "User",
            },
        )
        if created:
            super_user.set_password("admin")
            super_user.save()
            self.stdout.write("Created admin user (username: admin, password: admin)")

        # Create or get geo organization
        geo_organization = self._get_or_create_geo_organization(super_user)
        self.geo_organization = geo_organization
        self.stdout.write(f"Using geo organization: {geo_organization.name}")

        # Create MMC Hospital facility
        facility = self._create_mmc_facility(super_user, geo_organization)
        self.stdout.write(f"Created facility: {facility.name}")

        # Get doctor role
        try:
            doctor_role = RoleModel.objects.get(name="Doctor")
        except RoleModel.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("Doctor role not found. Please run sync_permissions_roles first.")
            )
            return

        self.stdout.write("=" * 60)
        self.stdout.write("DOCTOR CREDENTIALS")
        self.stdout.write("=" * 60)
        self.stdout.write(f"{'DEPARTMENT':<15} {'USERNAME':<25} {'PASSWORD':<15}")
        self.stdout.write("-" * 60)

        # Create departments and doctors
        for dept_config in DEPARTMENTS:
            # Create department
            department = self._create_department(
                super_user, facility, dept_config["name"], dept_config["description"]
            )
            self.stdout.write(f"Created department: {department.name}")

            # Create doctors for this department
            short_name = dept_config["short_name"]
            doctor_list = DOCTOR_NAMES[short_name]

            for i, doctor_info in enumerate(doctor_list):
                username = f"dr_{short_name.lower()}_{i + 1}"

                # Create doctor user
                doctor = self._create_doctor(
                    super_user,
                    username,
                    doctor_info["first_name"],
                    doctor_info["last_name"],
                    default_password,
                    department,
                    doctor_role,
                )

                self.stdout.write(f"{short_name:<15} {username:<25} {default_password:<15}")

                # Create schedulable resource and availability for the doctor
                self._create_doctor_schedule(super_user, facility, doctor)

        self.stdout.write("=" * 60)
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("MMC Hospital Setup Complete!"))
        self.stdout.write(f"Facility: MMC Hospital")
        self.stdout.write(f"Departments: BP, Sugar, Ortho (3 departments)")
        self.stdout.write(f"Doctors: 9 total (3 per department)")
        self.stdout.write(f"Availability: Created for the current week")
        self.stdout.write("")

    def _get_or_create_geo_organization(self, super_user):
        """Get or create a geo organization for MMC."""
        org = Organization.objects.filter(
            org_type=OrganizationTypeChoices.govt.value
        ).first()

        if org:
            return org

        org_spec = OrganizationWriteSpec(
            active=True,
            org_type=OrganizationTypeChoices.govt,
            name="Karnataka State Health",
        )
        org = org_spec.de_serialize()
        org.created_by = super_user
        org.updated_by = super_user
        org.save()
        return org

    def _create_mmc_facility(self, super_user, geo_organization):
        """Create MMC Hospital facility."""
        facility_spec = FacilityCreateSpec(
            geo_organization=geo_organization.external_id,
            name="MMC Hospital",
            description="Multi-Specialty Medical Center providing comprehensive healthcare services including Blood Pressure management, Diabetes care, and Orthopedic treatments.",
            longitude=77.5946,  # Bangalore coordinates
            latitude=12.9716,
            pincode=560001,
            address="123 MG Road, Bangalore, Karnataka 560001",
            phone_number=generate_unique_indian_phone_number(),
            middleware_address="",
            facility_type="Private Hospital",
            is_public=True,
            features=[1],
        )
        facility = facility_spec.de_serialize()
        facility.created_by = super_user
        facility.updated_by = super_user
        facility.save()
        return facility

    def _create_department(self, super_user, facility, name, description):
        """Create a facility organization (department)."""
        org_spec = FacilityOrganizationWriteSpec(
            active=True,
            name=name,
            description=description,
            facility=facility.external_id,
            org_type=FacilityOrganizationTypeChoices.dept,
        )
        org = org_spec.de_serialize()
        org.created_by = super_user
        org.updated_by = super_user
        org.save()
        return org

    def _create_doctor(
        self,
        super_user,
        username,
        first_name,
        last_name,
        password,
        department,
        role,
    ):
        """Create a doctor user and attach to department."""
        is_male = first_name in ["Rajesh", "Amit", "Vikram", "Suresh", "Arjun"]
        user_spec = UserCreateSpec(
            first_name=first_name,
            last_name=last_name,
            phone_number=generate_unique_indian_phone_number(),
            prefix="Dr.",
            suffix="MD",
            gender=GenderChoices.male if is_male else GenderChoices.female,
            password=password,
            username=username,
            email=f"{username}@mmchospital.com",
            user_type=UserTypeOptions.doctor,
        )
        user = user_spec.de_serialize()
        user.geo_organization = self.geo_organization
        user.created_by = super_user
        user.updated_by = super_user
        user.save()

        # Attach to department (facility organization)
        FacilityOrganizationUser.objects.create(
            organization=department,
            user=user,
            role=role,
        )

        # Attach to default internal organization if exists
        if department.facility.default_internal_organization:
            FacilityOrganizationUser.objects.create(
                organization=department.facility.default_internal_organization,
                user=user,
                role=role,
            )

        # Attach to geo organization
        OrganizationUser.objects.create(
            organization=self.geo_organization,
            user=user,
            role=role,
        )

        # Attach to role organization
        role_org = Organization.objects.filter(
            name="Doctor", org_type=OrganizationTypeChoices.role.value
        ).first()
        if role_org:
            OrganizationUser.objects.create(
                organization=role_org,
                user=user,
                role=role,
            )

        return user

    def _create_doctor_schedule(self, super_user, facility, doctor):
        """Create schedulable resource and availability for a doctor."""
        # Create or get schedulable resource
        schedulable_resource, created = SchedulableResource.objects.get_or_create(
            facility=facility,
            resource_type="practitioner",
            user=doctor,
        )

        if created:
            schedulable_resource.created_by = super_user
            schedulable_resource.updated_by = super_user
            schedulable_resource.save()

        # Create schedule for current week
        now = timezone.now()
        # Start from today
        valid_from = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # End in 7 days
        valid_to = valid_from + datetime.timedelta(days=7)

        schedule = Schedule.objects.create(
            resource=schedulable_resource,
            name=f"Dr. {doctor.first_name} {doctor.last_name} - Weekly Schedule",
            valid_from=valid_from,
            valid_to=valid_to,
            is_public=True,
            created_by=super_user,
            updated_by=super_user,
        )

        # Create availability for weekdays (Monday-Friday, 9 AM to 5 PM)
        # Create morning and afternoon slots
        availability_config = [
            {
                "name": "Morning Consultation",
                "slot_type": "appointment",
                "slot_size_in_minutes": 30,
                "tokens_per_slot": 2,
                "create_tokens": True,
                "reason": "Regular consultation hours",
                "availability": [
                    {"day_of_week": day, "start_time": "09:00:00", "end_time": "13:00:00"}
                    for day in range(0, 5)  # Monday to Friday (0-4)
                ],
            },
            {
                "name": "Afternoon Consultation",
                "slot_type": "appointment",
                "slot_size_in_minutes": 30,
                "tokens_per_slot": 2,
                "create_tokens": True,
                "reason": "Regular consultation hours",
                "availability": [
                    {"day_of_week": day, "start_time": "14:00:00", "end_time": "17:00:00"}
                    for day in range(0, 5)  # Monday to Friday (0-4)
                ],
            },
        ]

        for avail_config in availability_config:
            Availability.objects.create(
                schedule=schedule,
                name=avail_config["name"],
                slot_type=avail_config["slot_type"],
                slot_size_in_minutes=avail_config["slot_size_in_minutes"],
                tokens_per_slot=avail_config["tokens_per_slot"],
                create_tokens=avail_config["create_tokens"],
                reason=avail_config["reason"],
                availability=avail_config["availability"],
                created_by=super_user,
                updated_by=super_user,
            )

        self.stdout.write(f"  Created schedule for Dr. {doctor.first_name} {doctor.last_name}")
