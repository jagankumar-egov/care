# **Laboratory Module**

# **Overview**

## **1\. Document Information**

| Field | Placeholder |
| :---- | :---- |
| Module | Laboratory Module |
| Version | v1.0 |
| Date Created | 15-AUG-2025 |
| Last Updated | 15-OCT-2025 |
| Target Persona(s) | Doctors / Practitioners, Lab in-charge, Lab staff |

## **2\. Purpose**

The Laboratory Module streamlines the end-to-end diagnostic workflow in the CARE platform. It ensures accurate test configuration, smooth request initiation by doctors, and efficient processing by lab staff. This module brings consistency, compliance, and transparency to all lab-related operations.

## **3\. Scope**

* Covers: Setup of lab services and locations, specimen/observation/charge/activity definitions, creation of diagnostic service requests, lab processing, and report generation.

* Does Not Cover**:** Billing operations beyond charge definition, clinical diagnosis outside the lab scope, or third-party lab integrations.

## **4\. User Persona Context**

* **Admin** – Configures the foundational elements such as healthcare services, locations, specimen/observation definitions, charge items, and activity definitions.

* **Doctor”/Practitioners**”– Initiates service requests within patient encounters, defining clinical context and urgency and view diagnostic reports.

* **Lab Staff”/Technicians/Senior Reviewers”**  – Executes requests by collecting specimens, processing tests, entering results, and submitting reports for approval.

## **5\. Prerequisites**

* **System Requirements:** Users must have a CARE Staff account with appropriate role permissions (Admin, Doctor, or Lab Staff).

* **Knowledge Requirements:** Basic understanding of patient encounters, service request workflows, and role responsibilities.

## **6\. Expected Outcome**

* Admins have a structured lab configuration that supports all diagnostic workflows.  
* Doctors can raise accurate, role-linked diagnostic service requests.  
* Lab staff can process requests, record results, and ensure validated diagnostic reports are visible to doctors.

## **7\. Login (Admin, Doctor, or Lab Staff)** {#7.-login-(admin,-doctor,-or-lab-staff)}

Before accessing any Laboratory workflows, users must log in to the CARE Staff portal with the following steps:

1. Navigate to the **CARE Staff Login page** in your browser.  
2. Enter your **User ID** and **Password.**

3. Click **Login**.  
4. Select the appropriate **Facility** (if multiple facilities are available).

After successful authentication, you will be directed to the **Dashboard** based on your assigned role (Admin, Doctor, or Lab Staff).

#  **Laboratory Module-Admin Workflow** 

## **1\.  Document Information**

| Field | Placeholder |
| :---- | :---- |
| Module | Laboratory Module |
| Version | v1.0 |
| Date Created | 15-AUG-2025 |
| Last Updated | 15-OCT-2025 |
| Target Persona(s) | Admins  |

## **2\. Purpose**

This workflow enables administrators to configure laboratory and imaging services in CARE. It covers the creation of locations, healthcare services, and the definitions (Activity, Specimen, Observation, and Charge Item) that form the foundation of diagnostic workflows.

## **3\. Scope**

## **Covers:**

* Creating a lab location in a facility.  
* Setting up healthcare services.  
  Defining activity, specimen, observation, and charge item definitions.

**Does Not Cover:**

* Processing lab requests (handled by Lab Staff).  
* Ordering tests (handled by Doctors/Practitioners).

## **4\. User Persona Context**

Admins are responsible for setting up and maintaining the structural configurations required for laboratory operations. This ensures smooth coordination between doctors who order tests and lab staff who process them.

## **5\. Prerequisites**

**System Requirements:**

* CARE Admin account with configuration privileges.  
* Access to Facility, Healthcare Services, and Definition setup modules.

**Knowledge Requirements:**

* Understanding of lab workflows and services offered in the facility.  
* Familiarity with Activity, Specimen, Observation, and Charge Item setup.

## **6\. Expected Outcome**

After following this workflow, the facility will have fully configured lab and imaging services with all required definitions, ready for use in clinical workflows.

## **7\. Step-by-Step Instructions**

### **7.1 Add Lab Location**

Creating a lab location ensures that every diagnostic area *(e.g., Radiology, Biochemistry Lab, Pathology Room)* is accurately mapped within the facility. This allows services to be linked to the right physical or virtual space for smooth coordination and reporting. The step by step instruction dealing with how to set up healthcare services is listed below.

Log into the **CARE Staff portal as indicated in the overview section ([Login (Admin, Doctor, or Lab Staff)](#7.-login-\(admin,-doctor,-or-lab-staff\))) or if already logged in, follow the steps below:**

1. Navigate to **Settings → Location.**

     

2. View Existing Locations displayed.

Each entry shows the **Type** (e.g., Building, Ward)**, Status** (Active/Inactive), and **Availability (**Available or not).

3. Click on the **‘+ Add Location’** button at the top right.

4. Fill the **Location** Details.

   It contains:

* **Location Form**: Choose the type of location from the dropdown.   
* **Name**: Enter a unique name for the location.  
* **Description\*** (Optional): Provide any relevant clinical or administrative notes about this location.  
* **Statu**s: Choose the current setup status.  
  * Active: Available for use.  
  * Inactive: Not currently in use.  
  * Unknown: Status not defined yet.  
* **Operational Status**: Define the real-time usability status of the space,  
  * Operational: Ready for patient care.  
  * Closed: Temporarily shut.  
  * Housekeeping: Being cleaned.  
  * Isolated: Quarantine or infection control.  
  * Contaminated: Not safe for use.  
  * Unoccupied: Available but not in use.

5. Click **‘Create**’ to finalize the setup.

         

### **7.2 Add Healthcare Services**

Healthcare Services define the diagnostic or clinical services *(e.g., Biochemistry, X-Ray, Physiotherapy)* available in the facility. Setting them up ensures that lab requests are properly categorized and linked to the correct location for efficient operations. The step-by-step instruction dealing with how to set up healthcare services is listed below.

Log into the **CARE Staff portal as indicated in the overview section ([Login (Admin, Doctor, or Lab Staff)](#7.-login-\(admin,-doctor,-or-lab-staff\))) or if already logged in, follow the steps below:**

1. Navigate to **Settings → Healthcare Services**.


2. Open Healthcare Services, click the **'+ Add Healthcare Service**' button, located in the top-right corner, to create healthcare services.

3. Fill the **Basic Information.**

This section gathers the core details of the healthcare service which include:

* **Name:** Enter the official name of the service (*e.g., General Consultation, X-Ray, Physiotherapy Session).*  
* **Internal Type**: Select the appropriate internal classification from the dropdown.   
* **Extra Details**: Add any additional notes or context that might help other users understand the scope or purpose of this service.  
4. Select one or more physical or virtual **locations** from the dropdown where this service can be accessed.

5. Select **Icon** under **Styling\*** that visually represents the service(optional).

6. Click **Create** to activate the healthcare service in the system.

###                          

### **7.3 Specimen Definition**

Specimen Definition specifies the type of biological sample (e.g., blood, urine, tissue) that can be used for an in vitro diagnostic test, that is, a test performed on specimens taken from the human body.

For each specimen type it records:

* The material to be collected from the patient and the preparation/collection requirements.  
* The conditioned specimen that will be transported or analysed, including its container, additives, volume limits, and post-collection handling.

Log into the **CARE Staff portal as indicated in the overview section ([Login (Admin, Doctor, or Lab Staff)](#7.-login-\(admin,-doctor,-or-lab-staff\))) or if already logged in, follow the steps below:**

1. Navigate to **Settings \> Specimen Definition.**

2. **Navigate** to **Specimen Definition** to display the list of all specimen types defined for the facility.  It includes:

*You can use the filter option (available on the right panel) to sort it by status (i.e., Active, Draft, or Retired) for ease.*

* **Title**: Display name of the specimen*. (e.g., Liver Specimen, Ear Swab).*  
* **Status**: Indicates lifecycle state i.e, Active, Draft, or Retired.  
* **Description**: Brief narrative of the specimen and its intended diagnostic use.  
* **Actions**:  
  * **See Details**: Opens the detailed view of the selected specimen, where you can review all fields and make changes.

    Within the details view, you can also Edit the definition or Delete it if no longer applicable (subject to permissions and usage constraints).

3. Click **\+ Add Definition** at the top-right of the screen.

4. Fill the **Basic Information**

Fill in the basic field which describes the physical sample to be collected, which includes:

* **Title**: Clear, recognisable name. (*e.g. Whole Blood — CBC).*  
* **Slug**: A short, unique code for system use. (*e.g. cbc-blood)*.  
* **Status**: Set as Draft, Active, or Retired.  
* **Derived from URI**: Link to another definition if this one is derived (optional).  
* **Description**: Concise narrative describing the specimen and its diagnostic use. *(e.g., "Blood sample collected for complete blood count testing").*

5. Fill the **Specimen Details.**

Provide information on how the specimen is handled:

* **Type Collected**: Defines the physical type of the specimen collected from the patient, such as fluid, tissue, swab, or blood.  
* **Collectio**n: Describes the method used to collect the specimen. Examples include finger stick, venepuncture, or midstream urine.  
* **Patient Preparation**: Indicates any preparatory steps that must be followed before collection, such as fasting, oral rinse, or avoidance of certain medications.  
    
6. Fill the **Type Tested Information.**

This section defines additional characteristics related to the collected specimen and how it is intended to be used within a diagnostic service.

* **Is Derived**: Indicates whether the specimen is obtained from another specimen. For example, serum is derived from whole blood. Set this toggle to Yes if applicable.  
* **Single Use**: Identifies whether the specimen container is disposable. Enabling this ensures compliance with standard safety and hygiene protocols.  
* **Preference**: Marks the specimen as either Preferred or Alternate when multiple specimen options are available for the same test. Preferred specimens are prioritised for collection.  
* **Retention Time:** Defines the allowable duration that the specimen remains valid for testing post-collection, before degradation or rejection occurs *(e.g., 24 hours).*  
* **Requirements:** Lists any special handling or transport instructions. If none are required, display it as “No Requirement”.  
7. Fill the **Container Information.**

This section captures the configuration of the container in which the collected specimen is stored and transported.

* **Description**: Identifies the container used, such as Sterile 10 mL urine container or 5 mL EDTA tube. This ensures correct selection and preparation.

* **Cap:** Indicates the cap colour or label, useful for easy identification *(e.g., Lavender, Red, Yellow).*  
* **Capacity**: Defines the maximum volume the container can hold *(e.g., 10 mL*). This is critical for preventing overfill and ensuring sample safety.  
* **Minimum Volume**: Specifies the minimum amount of specimen required to perform valid testing *(e.g., 2 mL).* Collecting below this may result in test rejection.  
* **Preparation**: Lists any preparation steps before collection *(e.g., Pre-label the container, Invert gently after collection).*


8. Click **Save.**

### **7.4 Observation Definition**

Observation Definition represents the definitional aspects of a kind of observation. It describes the structure and constraints of a kind of observation that may be collected and recorded as part of a diagnostic or clinical workflow. It defines what is being measured, how it is measured, and how the result should be represented, including its data type, unit, method, and applicable reference ranges or components.

In the CARE platform, each Observation Definition acts as a reusable template for recording specific types of observations—such as Fasting Blood Glucose, Blood Pressure, or Hemoglobin level. These definitions ensure that every observation recorded across the system follows a format, making it easier for clinicians, laboratories, and downstream systems to interpret and process the results accurately. Once configured, these definitions serve as the foundation for generating structured observation records throughout the Facility.

Log into the **CARE Staff portal as indicated in the overview section ([Login (Admin, Doctor, or Lab Staff)](#7.-login-\(admin,-doctor,-or-lab-staff\))) or if already logged in, follow the steps below:**

1. Navigate to **Settings → Observation Definition.**

2. **Navigate** to **Observation Definition to** display the list of all observation types defined for the facility. 

It includes:

* **Title**: Name of the observation (e.g., CT Scan, Hemoglobin).  
* **Category**: Group Classification such as Laboratory, Vital Signs, Imaging.  
* **Status:** Indicates whether the observation is Active, Draft, or Retired.  
* **Data Type**: Format of the observation result. (Quantity, Boolean, Decimal, etc.)  
* **Actions:**

  * **See Details**: Opens the detailed view of the selected observation, where you can review all fields and make changes.

*You can use the filter option (available on the right panel) to sort it by status (i.e Active, Draft, or Retired)   and Category for ease.*

3. Click **\+ Add Definition** to create a new observation, or open See Details to edit an existing one.

     

4. Fill the **Basic Information.**

   

This section defines/describes the measurement/test result generated from that specimen, which includes:

* **Title:** Name of the observation as it will appear in the system *(e.g., Fasting Blood Glucose).*   
* **Slug**: A short, system-usable identifier *(e.g., fbg)*. This is used for internal referencing and must be unique.  
* **Description**: A brief explanation of what the observation measures or represents. *(e.g., “Measures the glucose concentration in fasting state”)*  
* **Status**: Indicates the availability state of the observation.  
  * Draft: Still under configuration.  
  * Active: Available for use.  
  * Retired: No longer in use.  
* **Category**: Groups the observation under a broader type such as Laboratory, Vitals, Procedure, Imaging etc.   
* **Data Type**: Specifies the format of the result that will be recorded, such as:  
  * Boolean: Yes/No  
  * Quantity: Numeric value with unit.  
  * Decimal: Numeric with decimals.  
  * String: Free text  
  * Integer: Whole number  
  * Date: A calendar date  
  * Date Time: Date and time together.  
* **LOINC Code**: Standardised code used for interoperable data exchange. If available, map the observation to a relevant LOINC code *(e.g. 2339-0 for Glucose \[Mass/volume\] in Blood).*


5. Fill the **Additional Details** (Optional)\*

This section is used to provide further clinical and procedural context for how the observation is collected:

* **Body Site**: Specifies the anatomical location relevant to the observation. *(e.g. Left Arm, Chest, or Structure of left deltoid muscle)*  
* **Method**: Describes the technique, device, or process used to generate the observation. *(e.g., Fluoroscopic venography, Manual inspection, Pulse oximeter)*  
* **Unit**: Defines the default unit of measurement to be used when entering results *(e.g.,mg/dL, bpm, mmHg, milligram (mg))*. This ensures consistency in result representation.

6. Click **\+ Add your first component** section if the observation needs to collect multiple values.

Some observations consist of multiple values or measurements grouped together under a single test. These are defined as components. 

*Examples include: Blood Pressure (Systolic \+ Diastolic), CBC Test (RBC, WBC, Platelet Count, etc.)*

7. Click **Add Component** after defining the components.

           For each component:

* Enter **Code** (often a SNOMED or observation code)  
* Select **Data Type.** (Quantity, String, etc.)  
* Specify the **Unit,** based on data type *(e.g. milligram (mg), percent (%)).*

You can add as many components as required to represent the complete observation structure.

8. Click **Create.**

### 

### **7.5 Charge Item Definition**

A Charge Item Definition represents the pricing and billing logic applied to services, procedures, and diagnostic activities offered within a Facility. It defines the base price, taxes, applicable discounts, and billing conditions associated with a particular test or service.

These definitions ensure transparency in how charges are calculated across departments, helping the system generate accurate invoices based on predefined pricing rules.

Charge Item Definitions are applied by the billing engine when evaluating Charge Items within an account or encounter, ensuring that pricing reflects real time rules, discounts, and taxes associated with each service.

Log into the **CARE Staff portal as indicated in the overview section ([Login (Admin, Doctor, or Lab Staff)](#7.-login-\(admin,-doctor,-or-lab-staff\))) or if already logged in, follow the steps below:**

1. Navigate to **Settings → Charge Item Definition**

2. Navigate through the dashboard to manage pricing definitions. 

It contains

* **Title**: Name of the item or service *(e.g., Complete Blood Count)*  
* **Status** : Indicates lifecycle stage (Draft, Active, Retired)  
* **Description** : Summary of the item’s purpose.  
* **Actions**  
  * **See Details**: Opens the detailed view of the selected definition, where you can review all fields and make changes.

*You can use the filter option (available on the right panel) to sort it by status(i.e. Active, Draft or Retired)   for ease.*

3. Click **\+ Add Definition** to create a new observation, or open **See Details** to edit an existing one.

4. Fill the **Basic Information**

This section identifies the billing item and its status.

* **Title** : The name of the charge  item or service *(e.g., “Complete Blood Count”).*  
* **Slug** : Short, system-unique identifier *(e.g., cbc-test).*

5. Fill the **Additional Details**

This is used to provide contextual or functional information about the charge item.

* **Description :** A brief explanation of what this charge represents. *For example: Blood panel test used to evaluate overall health.*  
    
* **Purpose** : Functional categorisation or intended use-case of the item. *E.g., Laboratory Test, Emergency Procedure.*  
    
* **Derived from URI :** A reference to a source item or service if this definition is based on another.  
    
6. Fill the **Pricing Component**.  
* **Base Price** : Enter the flat fee charged for this item *(e.g., ₹400).* This represents the unadjusted rate.

*  **Discounts :** Choose from predefined discounts configured in the system. *Examples may include In-house staff discount, Student pricing, CSR Program discounts etc.*


* Total Discount is automatically calculated based on selected discount percentages. Also,multiple discounts can be selected if applicable.


* **Taxes**: Select the applicable Taxes

* CGST – Central Goods and Services Tax  
* SGST – State Goods and Services Tax  
* IGST – Integrated Goods and Services Tax

You can apply applicable tax components based on regulatory requirements, each tax can be defined with a fixed percentage.

7. Review the **Price Summary**

This section reflects the computed summary of the final charge based on all configured inputs.

* **Base Price** : From Pricing Component.  
* **Total Discount** : Aggregate from selected discounts.  
* **Total Tax** : Combined tax amounts (CGST \+ SGST \+ IGST).  
* **Final Price** : Automatically calculated net payable amount.

This helps you double-check the final cost before saving.

8. Click **Create**  
   

### **7.6 Activity Definition** 

An Activity Definition is a shareable, consumable description of some activity to be performed. It may be used to specify actions to be taken as part of a workflow, order set, or protocol, or it may be used independently as part of a catalogue of activities such as orderables.

Log into the **CARE Staff portal as indicated in the overview section ([Login (Admin, Doctor, or Lab Staff)](#7.-login-\(admin,-doctor,-or-lab-staff\))) or if already logged in, follow the steps below:**

1. Navigate to **Settings → Activity Definition.**  
 


2. Navigate through the page which lists all existing activity definitions.

* **Title:** The name of the service (e.g., Liver Function Test).  
* **Category**: The classification group (e.g., Laboratory, Procedure, Imaging).  
* **Status**: Indicates whether the activity is Active, Draft, or Retired.  
* **Kind:** The request type, which is fixed as Service Request.  
* **Actions**: Includes See Details, from which the activity can be edited or deleted.

*You can use the filter option (available on the right panel) to sort it by status (i.e.,  Active, Draft, or Retired)   and category for ease.*

3. To create a new entry, click **\+ Add Definition**.

4. Fill the **Basic Information.**

It includes:

* **Title**: The name representing the clinical service or test (*e.g., "Liver Function Test"*).  
* **Slu**g: A short, system-unique identifier used internally (*e.g., lft for Liver Function Test*).  
* **Description**: A brief narrative that explains the clinical intent of the activity.  
* **Usage**: Indicates the intended use context, for example, outpatient, emergency, or internal referrals only.  
* **Status**: The lifecycle state of the activity, select from Draft, Active, or Retired.  
* **Category**: The type of service offered  which includes Laboratory, Procedure, Imaging, Survey, Therapy, etc.  
* **Kind**: The kind of request used to initiate this activity. In the CARE platform, this is set to Service Request.  
* **Derived from URI\*:** (Optional) A URI reference to another Activity Definition from which this definition is derived.  
* **Code**: A clinical code representing the defined activity, such as a SNOMED CT code.  
   *Example: 107963000 – Excision of liver (SNOMED CT).*

5. Fill the **Additional Details**.\*

This section allows for further clinical specificity.It includes:

* **Body Site**: Indicates the anatomical site where the activity is performed, if relevant. *For example: Right arm, Liver, or Anterior chest wall.*

6.  Specify the **Requirements.**

* **Specimen Requirements**: Select one or more predefined Specimen Definitions that must be collected to perform this activity. These definitions ensure standardisation in how samples are collected and handled.  
* **Observation Requirements**: Choose the relevant Observation Definitions that this activity is expected to produce or require. These may include lab results, imaging findings, or other measurable values.  
* **Charge Item Definition:** Link the Charge Item Definition that governs pricing for this activity. The system will use this reference to apply correct billing, taxes, and discounts.  
* Add the **location** where the activity is to be performed.

7. Specify the **Diagnostic Report** for the activity.

*  This may be a LOINC or SNOMED CT code that classifies the report generated as part of the service.

8. Click **Create.**

## **8\. Error Handling/Common Issues**

| Error / Issue | Possible Cause | Resolution |
| ----- | ----- | ----- |
| Unable to link Lab Location to a Facility. | Missing permissions or incorrect facility mapping. | Verify Admin role permissions; re-map the lab location to the correct facility. |
| Healthcare Service not saving. | Required fields (name, type, category) not filled. | Enter all mandatory details before saving. |
| Activity Definition missing in Service Request dropdown. | Activity not created or set to Retired. | Create/activate Activity Definition under Admin settings. |
| Specimen Definition not available for selection. | Specimen not configured or inactive. | Add the specimen type and set it to Active. |
| Observation fields showing incorrectly in reports. | ObservationDefinition not configured properly. | Correct or update observation definition with right units and codes. |
| Charge Item not linked to service. | Charge Item not mapped to the Activity Definition. | Map the correct charge item while configuring the activity. |
| Duplicate Activity Definitions created. | Same service added multiple times. | Retire duplicates and keep one active, valid definition. |
| System not allowing changes to existing configuration. | Item already in use (linked to encounters/reports). | Retire old configuration and create a new version instead of editing live items. |

# **Laboratory Module- Doctor Workflow**

# **1\. Document Information**

| Field | Placeholder |
| :---- | :---- |
| Module | Laboratory Module |
| Version | v1.0 |
| Date Created | 15-AUG-2025 |
| Last Updated | 15-OCT-2025 |
| Target Persona(s) | Doctors / Practitioners |

## **2\. Purpose**

This flow is designed to help doctors order diagnostic tests and access results directly within CARE. It ensures that test requests are consistent, easy to track, and linked to the patient’s encounter, while also providing a clear way to review finalized reports that support timely clinical decisions.

## **3\. Scope**

**Covers:**

* Ordering laboratory and imaging tests as part of a patient encounter.  
* Viewing diagnostic reports after they have been completed and approved.

**Do Not Cover:**

* Configuration of services or definitions (covered in Admin Flow).  
* Specimen collection, test execution, and validation (covered in Lab Staff Flow).

## **4\. User Persona Context**

Doctors and Practitioners use this flow during patient consultations. They prescribe tests, provide preparation instructions where needed, and later review reports to confirm diagnoses or adjust treatment plans. Their role in CARE connects the patient’s clinical journey with the laboratory process, ensuring every decision is backed by accurate diagnostic data.

### **4.1 Navigation for Doctors**   {#4.1-navigation-for-doctors}

1. From the sidebar “**Patients**”, click on **“Encounters”.**

2. Click **View Encounter** to open the encounter dashboard.

.

## **5\. Prerequisites**

**System Requirements:**

* CARE Staff account with **Doctor/Practitioner** role assigned.  
* Access to **Encounters** and **Service Request** modules.

**Knowledge Requirements:**

* Familiarity with prescribing diagnostic tests.  
* Ability to interpret and review diagnostic reports.

## **6\. Expected Outcome**

After following this workflow, doctors will be able to:

* Prescribe and submit lab or imaging test requests during patient encounters.  
* Access completed diagnostic reports for clinical interpretation and decision-making.

## **7\. Step-by-Step Instructions**

###  **7.1 How to Initiate a Service Request in the System** {#7.1-how-to-initiate-a-service-request-in-the-system}

In a clinical setting, doctors frequently request services such as laboratory tests, imaging procedures, home care visits, or diagnostic panels. In the CARE platform, these services are formally represented as Service Requests linked to a predefined Activity Definition.

This workflow explains how a doctor can initiate a structured Service Request from within a patient’s active encounter record.

Log into the **CARE Staff portal as indicated in the overview section ([Login (Admin, Doctor, or Lab Staff)](#7.-login-\(admin,-doctor,-or-lab-staff\))) or if already logged in, follow the steps below:**

1. After logging in, follow these steps ([**Navigation for Doctors**](#4.1-navigation-for-doctors)).  
2.  Select **Service Request** from the dropdown.

 

3. Configure the **Service Request,** which is a formal request in CARE raised by a Doctor for a specific clinical service, such as a laboratory test, imaging scan, or procedure. The Doctor is the primary user who initiates the request, while Lab Staff and other teams act upon it once generated.  
 


4. Select **Activity definition** under Service Request and fill the remaining details.

It includes:

* **Priority:** Indicates the urgency of the service request. Options includes:  
* Routine  
* Urgent  
* ASAP  
* Stat  
    
* **Body Site**: Specifies the anatomical location where the procedure or sample collection is to occur. *(e.g., Right arm, Chest wall)*

* **Patient Instructions:** Free-text field to capture any instructions the patient must follow before or during the procedure. *(e.g., Fast for 8 hours before sample collection).*  
    
* **Notes**: Internal remarks for the care team; not visible to the patient. Useful for clarifying clinical context or coordination.

Multiple service requests may be created  by clicking the **Add** button. Submit the Request.

5. Click **Submit .**

The newly created Service Request is now recorded within the encounter and will appear under the Service Requests tab for processing by the appropriate clinical or diagnostic team.

### **7.2 Viewing a Patient’s Diagnostic Report**

Once a diagnostic service has been completed and results have been reviewed and approved, the corresponding Diagnostic Report becomes available within the patient’s encounter. This report consolidates the outcome of one or more clinical observations, along with interpretive insights and reference standards, enabling the requested doctor to make timely and informed decisions.

**Note:** The doctor can view a diagnostic report only when it's approved by a senior reviewer in the lab.  
See how it’s approved [here.](#7.4-how-to-verify-a-report)

Each report is contextually linked to the encounter, the underlying service request, and the observations performed.

Log into the **CARE Staff portal as indicated in the overview section ([Login (Admin, Doctor, or Lab Staff)](#7.-login-\(admin,-doctor,-or-lab-staff\))) or if already logged in, follow the steps below:**

1. After logging in, follow these steps ([**Navigation for Doctors**](#4.1-navigation-for-doctors)).  
2. Inside th**e Encounter dashboard**, click the **Diagnostic Reports.**  
   

3. Click **View Details**  to review Report Details.

4. Review the Diagnostic Report.  
   

The report contains:

* **Patient Information**: Displays the patient’s full name, DOB/age, and other demographic details relevant to the report context.  
* **Test Name**: Indicates the name of the diagnostic service performed — *for example, Complete Blood Count (CBC), Electrocardiogram (ECG), or Liver Function Test.* This corresponds to the Activity Definition that was originally selected during service request initiation.  
* **Category**: Specifies the type of service performed  such as Laboratory, Imaging, or Pathology. This helps classify the report within the broader care workflow.  
* **Status**: Reflects the current lifecycle state of the report typically Completed or Approved, indicating that the report has been finalized and verified by an authorized reviewer.  
* **Conclusion**: A clinical summary of the result interpretation such as Normal, Abnormal, or Critical. This field may also include coded flags that represent clinical severity or actionability.

The test result contains:

* **Name** of the test  
* **Results**: Lists individual observations recorded as part of the diagnostic test. Each result includes:  
* **Reference Range**: Normal value interval for clinical comparison.  
* **Interpretation**: Optional remarks or insights provided by the lab reviewer to assist the requesting doctor.

5. Click **Print** to generate a PDF version of the Diagnostic Report.

## **8\. Error Handling / Common Issues**

|  |  |  |
| ----- | ----- | ----- |
| **Error / Issue** | **Possible Cause** | **Resolution** |
| Patient encounter not found in the Encounters tab. | Encounter not created or patient registered under another facility. | Create a new encounter or switch to the correct facility. |
| Unable to open patient encounters. | Encounter closed or archived. | Reopen the encounter or create a new one if needed. |
| Service Request form not loading inside encounter. | Form not assigned to that encounter type. | Ask Admin to enable the Service Request form for the encounter type. |
| Diagnostic Report not opening. | Report still under review or not linked to encounter. | Confirm with Lab Staff; wait until the report is verified and linked. |
| Report shows mismatch with ordered test. | Wrong service request linked to encounter. | Ask Lab Staff to retire incorrect reports and regenerate the correct ones. |
| Conclusion field missing in report. | Report template not configured with conclusion field. | Ask the Admin/Lab Supervisor to update the report template. |
| Report language unclear or overly technical. | Lab staff used raw observation values only. | Request LabStaff to add interpretation/remarks in plain terms. |

# **Laboratory Module-Lab Staff Module**

## **1\. Document Information**

| Field | Placeholder |
| :---- | :---- |
| Module | Laboratory Module |
| Version | v1.0 |
| Date Created | 15-AUG-2025 |
| Last Updated | 15-OCT-2025 |
| Target Persona(s) | Lab in charge, lab staff |

## **2\. Purpose**

The goal of this workflow is to help Lab Staff , Technician & Senior Reviewers to handle test requests from doctors, collect the right specimens, enter the results, and make sure the final report is approved. The whole point is to get reliable test results back to the doctor quickly so patients can be treated without delay.

## **3\. Scope**

Covers:

* Checking and opening service requests raised by doctors.  
* Collecting specimens and recording collection details.  
* Processing specimens and entering test results.  
* Generating diagnostic reports.  
* Verifying reports before they are visible to doctors.

Does Not Cover:

* Creating or configuring services (Admin responsibility).  
* Placing service requests (Doctor responsibility).  
* Approving or interpreting results (Doctor responsibility).

## **4\. User Persona Context**

The users of this workflow are laboratory staff and senior lab staff. Lab staff are responsible for checking new service requests, collecting and processing specimens, and recording results in CARE. Senior lab staff act as reviewers — they go through the reports prepared by the team, verify the accuracy of the results, and approve them before doctors can view them. Together, they ensure that every diagnostic request is handled properly, results are reliable, and reports are ready for doctors to use in patient care.

### **4.1 Navigation for Lab Staff** {#4.1-navigation-for-lab-staff}

1. Under **Service**, the list of healthcare services offered by the Facility is seen. *(e.g., Biochemistry, Microbiology, Radiology).*

2. Locate the service you are responsible for and click **View Details**.

3. Click **View Requests** to access the queue of service requests relevant to that department

4. View and Filter Active Service Requests*. A service request is a request made by a user to the system for a specific service.*

You will now see a table of submitted requests. Each row represents a single Service Request and includes:

* **Patient Name**: The patient for whom the request was raised.  
* **Service Type**: The ordered service, linked to its Activity Definition.  
* **Priority**: Indicates urgency (Routine, Urgent, ASAP, Stat).  
* **Status**: Pending, In Progress, or Completed.

*Use the filter option (available on the right panel) to sort and view requests based on their priority.*

5. Click **See Details** to open and manage the request.

## **5\. Prerequisites**

**System Requirements:**

* CARE Staff account with **Lab Staff** role assigned.  
* Access to the Laboratory **module** in the facility.

**Knowledge Requirements:**

* Familiarity with specimen collection and safety protocols.  
* Ability to process specimens and enter results in CARE.  
* For senior lab staff: ability to review and verify diagnostic reports.

## **6\. Expected Outcome**

After following this workflow, lab staff will be able to check service requests, collect and process specimens, and generate diagnostic reports within CARE. Senior lab staff will successfully review and verify these reports, making them available for doctors to access and use in patient care.

## **7\. Step-by-Step Instructions**

### **7.1 How to Check a Service Request**

In the CARE platform, each medical test or diagnostic procedure requested by a doctor is formalized as a Service Request, tied to a predefined Activity Definition. This Activity Definition outlines the required specimen(s), observation(s), and expected reporting logic. Once a request is submitted, the laboratory or designated facility team is responsible for executing the service — from reviewing the request, collecting and processing specimens, recording results, and submitting the final diagnostic report for approval.

Before that, a service request must first be processed by the doctor to allow verification and further action by the staff.

Here’s how doctors initiate a [service request.](#7.1-how-to-initiate-a-service-request-in-the-system)

Log into the **CARE Staff portal as indicated in the overview section ([Login (Admin, Doctor, or Lab Staff)](#7.-login-\(admin,-doctor,-or-lab-staff\))) or if already logged in, follow the steps below:**

1. After logging in, follow these steps ([Navigation for lab Staff](#4.1-navigation-for-lab-staff)).  
2. Review the **Request** Details.

Inside the detailed request view, carefully verify the following:

* **Priority**: To determine urgency of fulfillment.  
* **Specimen:** As defined by the associated Specimen Definition.  
* **Observation Definition**: The expected observations that must be recorded.  
* **Requested Doctor**: The doctor who submitted the request.  
* **Payment or Billing Status**: The status of payment can be viewed here.

It’s essential to confirm that the request is complete and accurately configured before initiating any clinical or laboratory action.

### **7.2 How to Collect Required Specimen(s)**

Log into the **CARE Staff portal as indicated in the overview section ([Login (Admin, Doctor, or Lab Staff)](#7.-login-\(admin,-doctor,-or-lab-staff\))) or if already logged in, follow the steps below:**

1. After logging in, follow these steps ([Navigation for lab Staff](#4.1-navigation-for-lab-staff)).  
2. Scroll to the **Specimen** section of the request.

3. Click **\+Collect Specimen.**

4. Fill out the collection form with the following fields:

* **Date and Time of Collection**  
* **Quantity and Unit** *(e.g., 5 mL, 2 swabs)*  
* **Body Site**: The anatomical location from which the specimen is to be collected *(e.g., Left Arm, Throat).*  
* **Fasting Status**: Mark as Yes or No.  
* **Fasting Duration\***: Duration in hours if applicable.  
* **Storage Information:** Instructions such as Refrigerated at 2–8°C.


5. Cross-check the **Container Requirements** configured in the linked Specimen Definition to ensure correct handling *(e.g., EDTA tube, Sterile swab).*  
6. Click **Collect**, once verified.

7. A **QR code** will be automatically generated for the specimen. This can be printed and affixed to the physical sample to support tracking, identification, and laboratory integration.

8. Click **Process Specimen** to choose specimen steps performed on the Specimen (If Needed).

    **9\.** Click to the Specimen **Processing Step**, if the sample needs to go through any processing (like centrifugation or preparation).**10\.** Click **Add** in the Add Processing Step.

You may enter multiple steps if the specimen undergoes a multiphase process.

### **7.3 How to generate a Report**

Log into the **CARE Staff portal as indicated in the overview section ([Login (Admin, Doctor, or Lab Staff)](#7.-login-\(admin,-doctor,-or-lab-staff\))) or if already logged in, follow the steps below:**

1. After logging in, follow these steps ([Navigation for lab Staff](#4.1-navigation-for-lab-staff)).  
2. After collection and processing, navigate to the **Test Result** Generation section.  
3. Choose the appropriate **Diagnostic Result Type**, linked to the Observation Definitions from the Activity.

4. Click **Create Report.**

5. Enter the **Observation Value (**Clinical Findings).

* **Result**: Measured value or qualitative outcome.  
* **Abnormal Flag**: If applicable, mark if the result is outside normal range.  
* **Conclusion**: Optional clinical interpretation or summary.


6. After reviewing the inputs, click **Save Result.**

### **7.4 How to Verify a Report** {#7.4-how-to-verify-a-report}

1. Once the result is recorded, review it in the Result **Review  tab.**

2. The report is routed to a designated **Senior Reviewer** (e.g.*, Department Head or Approver*).  
3.  The reviewer reviews the results, clinical summary, and observation details.  
4.  Upon validation, they click **Approve Results.**

## 

## 

## **8\. Error Handling/Common Issues**

| Error / Issue | Possible Cause | Resolution |
| ----- | ----- | ----- |
| Service Request assigned to the wrong facility. | Request created under a different facility. | Switch to the correct facility or ask the doctor to resubmit under the right one. |
| Cannot find patient record linked to Service Request. | Patient encounter closed or mismatched. | Reopen the encounter or request a doctor to map the correct encounter. |
| Barcode/Specimen ID not generated. | Specimen definition missing barcode rule. | Contact Admin to configure specimen ID/barcode generation. |
| Unable to record specimen collection time. | Invalid date/time format entered. | Enter the time in the correct system format (DD-MMM-YYYY HH:MM). |
| Processing screen not loading. | Network issue or lab module not synced. | Refresh, clear cache, or retry after system sync. |
| The observation field shows the wrong units. | Incorrect mapping in Observation Definition. | Ask Admin to update observation configuration with correct units. |
| Calculated values not appearing in the report. | Derived fields not configured. | Report to Admin to set up calculation rules for the test. |
| Verification button disabled. | The user does not have reviewer/approver permissions. | Ensure senior staff roles with verification rights are assigned. |
| Report approval delayed. | Reviewer not notified or notification rules disabled. | Enable alerts/notifications for pending verifications. |
| Finalized report showing formatting issues. | Report template not configured properly. | Contact Admin to update or fix the diagnostic report template. |

