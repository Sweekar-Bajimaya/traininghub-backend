# **Product Requirements Document (PRD)**

# **Product Overview**

The product is about Merojob Training that is used to provide training to users in need. It's open to all including users from Merojob. This product would come under Merojob. So users (jobseekers and Employers) can take this service without registration. 

In the MVP, learners do not log in: they browse trainings and send an **enquiry** to the institute. Learner accounts and formal applications (apply / approve / reject / capacity) are planned for a later phase. Only institutes and Merojob administrators have accounts.

Verified training institutes can create and publish training programs under relevant categories. Users can browse available training and enquire about it based on their availability and interests.

Training can be conducted through delivery modes:

* Physical/ In-person  
* Online
* Hybrid (Online + Physical)

# **Problem Statement**

Users can currently have limited access to centralized training platform where they can:

* Discover relevant professional training programs.

* Compare different training opportunities.

* Apply for training programs.

* Find both online and physical training.

* Track their training participation.

* Discover training opportunities related to their career interests.

Training instructors also need a platform where they can:

* Discover relevant professional training programs.

* Compare different training opportunities.

* Apply for training programs.

* Find both online and physical training.

* Track their training participation.

* Discover training opportunities related to their career interests.

# **Product Goal**

* Provide users with a centralized platform to discover training opportunities

* Allow training providers to create and manage training programs

* Allow users to enquire about relevant training programs (MVP) and apply/enroll in them (later phase).

* Integrate training activity with existing Merojob ecosystem.

# **Similar Products**

Following are similar products with their own use case and usability:

* Broadway Infosys: [Broadwayinfosys](https://broadwayinfosys.com/)

* Skill Training Nepal: [SkillTrainingNepal](https://skilltrainingnepal.com/)

# **Target users** 

1. ## **Learner / Participant**

   User who wants to discover and participate in training programs. They can:

* Find relevant training

* Filter training by category and mode

* View training details 

* Attend training 

* Receive completion/certification information.

2. ## **Training Provider** 

   A verified training institute. A staff user belongs to one institute only. An institute can have several staff users (an owner plus staff the owner invites) and several locations. They can:

* Create training programs

* Publish training opportunities

* Define schedules and requirements 

* Follow up enquiries (review applicants and manage participants in a later phase)

* Manage the institute profile, locations and verification documents

3. ## **Training Administrator**

   Merojob Administrator responsible for managing the overall training platform.  
   They can:

* Review training submissions

* Approve/Reject trainings

* Manage categories 

* Manage user/providers (approve, reject, request information, suspend institutes)

* Monitor enquiries (applicants in a later phase)

There is exactly one Super Admin, who can do everything and grants other admin users limited permissions, for example handling enquiries or managing account status.

# **User Role**

| Role | Description |
| :---- | :---- |
| Learner / Participants | Browses trainings and sends enquiries without an account (applies and participates in a later phase) |
| Training providers (institute owner / staff) | Creates and manages trainings and follows up enquiries |
| Admin | Manages the platform within the permissions granted by the Super Admin |
| Super Admin (one) | Full access; grants permissions to admins |

# 

# **Product Scope** 

## **MVP Scope**

**Training Management** 

* Create / Edit / Publish training

* Publish / Unpublish training

* Training approval / cancellation / completion

**Training Discovery**

* Training listing 

* Training Detail page

* Category filtering 

* Search 

* Location filtering 

* Date filtering

**Institutes**

* Institute registration with verification documents

* Admin approval / rejection / request for information / suspension

* Institute profile with several locations (see Institute Locations)

* Invite additional staff

**Training Enquiry**

* Enquire about a training without an account (name, phone, optional email, message)

* Enquiry status handled by the institute (New, Contacted, Converted, Closed)

* "My enquiries" for the visitor on the same browser, kept for 90 days

**Training Modes** 

* Physical 

* Online

* Hybrid (Online + Physical)

## **Later phase (not in MVP)**

**Training Application** 

* Apply for training (requires learner account)

* Application status

* Application withdrawal / approval / rejection

* Participants Management

**Reviews and ratings** (requires learner account)

# **Training Schedule** 

A training session may contain one or multiple sessions. It should include:

* Start date 

* End date 

* Duration

* Session Schedule

* Time zone: all sessions are in Nepal Time (NPT), including online trainings

* Registration deadline 

# **Training Categories** 

Every training must belong to a category For example:

**Technology**  
├── Python   
├── JavaScript   
├── Web Development   
└── Data Science

**Professional Development**   
├── Communication   
├── Leadership   
├── Interview Skills   
└── Career Development

# **Training Application (later phase)**

## **Application Flow**

User  
 ↓  
Browse Trainings  
 ↓  
View Training  
 ↓  
Apply  
 ↓  
Application Created  
 ↓  
Provider Reviews Application  
 ↓  
Approved / Rejected / Waitlisted  
 ↓  
User Notified

# **Application Status (later phase)**

Following would be application status:

* PENDING

* APPROVED

* REJECTED

* CANCELLED

* COMPLETED

# **Search & Discovery**

User should be able to search and filter trainings by:

## **Search** 

* Training title 

* Instructor Name

* Keywords

## **Filter**

* Category

* Sub-Category

* Training mode 

* Location

* Price

* Start Date

* Duration

* Availability (seats not yet used by converted enquiries)

* Provider

# **User Stories** 

## **Learner / User**

* As a Merojob user, I want to browse available training so that I can find training relevant to my career.

* As a learner, I want to filter training by category so that I can find relevant training quickly.

* As a learner, I want to filter training by online/physical mode so that I can choose a convenient training format.

* As a learner, I want to apply for training so that I can participate in it.

* As a learner, I want to see my application status so that I know whether I have been accepted.

## **Trainer / Instructor**

* As a training provider, I want to create training so that users can discover and apply for it.

* As a training provider, I want to define the training mode so that users know whether it is online or physical.

* As a training provider, I want to review applicants so that I can select appropriate participants.

* As a training provider, I want to manage training sessions so that participants know when the training takes place.

## **Administrators**

* As a training administrator, I want to review submitted training so that only approved training is published.

* As an administrator, I want to manage training categories so that training are properly organized.

# **User Training Dashboard**

MVP: a "My enquiries" list per browser, kept for 90 days. The full dashboard below needs learner accounts and is a later phase.

Users should have a dedicated training section.

My Trainings

├── Applied  
├── Upcoming  
├── Ongoing  
├── Completed  
└── Cancelled

Each training should show:

* Training title

* Provider

* Training mode

* Schedule

* Application status

* Completion status

# **Training Provider Dashboard**

Providers should have a dedicated dashboard.

**Training Provider Dashboard**  
├── Overview  
├── My Trainings  
├── Create Training  
├── Enquiries (Applications in a later phase)  
├── Participants  
├── Sessions  
└── Reports

Provider should be able to:

* Create/Update/Delete Training

* Submit training for approval

* Approve / Reject applications

* Manage participants & Sessions

# **Training Enquiry Rules (MVP)**

* No login is required to send an enquiry.

* Enquiries are protected by a captcha and rate limiting.

* Only approved trainings of approved institutes can receive enquiries.

* A visitor can see their own enquiries on the same browser for 90 days.

# **Training Application Rules (later phase)**

Examples of business rules:

* A user must be authenticated before applying for training.

* A user cannot submit multiple active applications for the same training.

* A user cannot apply after the registration deadline.

* A user cannot apply when the training is cancelled.

* A training provider cannot approve more participants than the configured capacity.

* Only approved participants can attend the training.

# **Institute Locations**

An institute can operate from several locations (for example branches in different cities), and its trainings can take place at different ones.

* An institute has one or more locations chosen from the managed Nepal province / district / city list, each with an address.

* One location can be marked as the main office.

* A physical or hybrid training is held at exactly one of the institute's locations; an online training has no physical location.

* Visitors can filter trainings by the location where the training is held.
