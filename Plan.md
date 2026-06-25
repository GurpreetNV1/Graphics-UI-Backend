# Internal Creative Request Management System Plan

## Project Objective

Create an internal platform to streamline communication and collaboration between:

* Australia Team
* Graphics Team

The platform will replace unstructured WhatsApp-based communication with a centralized workflow system.

---

# Current Workflow

## Existing Process

1. Australia Team sends requirements over WhatsApp
2. Graphics Team receives scattered messages/files
3. Requirements are discussed manually
4. Final creatives are shared again over WhatsApp
5. Captions and revisions are shared separately

---

# Problems in Current Workflow

* Unstructured communication
* Requirements get lost in chats
* Files difficult to track
* No centralized storage
* No status tracking
* Difficult revision management
* Delays in communication
* No workflow visibility

---

# Proposed Solution

Develop an internal web-based system where:

* Australia Team creates creative requests
* Graphics Team manages and fulfills requests
* All files are stored centrally
* Deliverables are uploaded within the platform
* Workflow statuses are tracked properly

---

# System Overview

```text
Australia Team Portal
          ↓
Create Creative Request
          ↓
Database + Google Drive Storage
          ↓
Graphics Team Dashboard
          ↓
Upload Final Deliverables
          ↓
Approval / Completion Workflow
```

---

# Core Features

# 1. Authentication System

## Purpose

Secure internal access.

## Recommended Approach

* Google Workspace Login
* Only company email accounts allowed

---

# 2. Creative Request Creation

## Australia Team Features

Users can:

* Create new requests
* Upload videos/files
* Add requirements
* Add captions
* Set deadlines
* Set priorities

---

# Request Form Fields

```text
Title
Description
Reference Links
Platform
Priority
Deadline
Caption Requirements
Hashtags
Video Upload
Reference Image Upload
```

---

# 3. File Upload System

## Purpose

Store and manage all creative assets.

## Storage Solution

* Google Drive API

## Advantages

* Existing Workspace available
* Centralized storage
* Easy sharing
* Scalable
* Permission management

---

# Suggested Drive Structure

```text
Creative-Requests/
    Request-ID/
        Raw-Files/
        Final-Deliverables/
        Thumbnails/
        Captions/
```

---

# 4. Graphics Team Dashboard

## Features

Graphics team can:

* View assigned tasks
* Filter requests
* Change request status
* Download raw files
* Upload final deliverables
* Add captions
* Add comments

---

# Request Status Workflow

```text
Pending
In Progress
Review
Changes Requested
Completed
Rejected
```

---

# 5. Deliverables Module

## Graphics Team Uploads

* Final videos
* Posters
* Captions
* Hashtags
* Thumbnails

---

# 6. Review & Approval System

## Australia Team Can

* Review completed work
* Request revisions
* Approve final deliverables

---

# 7. Notifications System (Future Enhancement)

Potential notifications:

* Email notifications
* Deadline reminders
* Task assignment alerts
* Status update alerts

---

# Recommended Tech Stack

# Frontend

## Recommended

* React.js
* Tailwind CSS

---

# Backend

## Recommended

* Node.js
* Express.js

---

# Database

## Recommended

* MongoDB

## Reason

* Flexible schema
* Fast development
* Ideal for internal tools

---

# File Storage

## Recommended

* Google Drive API

---

# Authentication

## Recommended

* Google OAuth
* Workspace domain restriction

---

# Suggested Database Schema

# Users Collection

```js
{
  name,
  email,
  role,
  createdAt
}
```

---

# Requests Collection

```js
{
  title,
  description,
  platform,
  priority,
  deadline,
  status,
  requestedBy,
  assignedTo,
  rawFiles: [],
  finalFiles: [],
  captions,
  comments: [],
  createdAt,
  updatedAt
}
```

---

# User Roles

## Australia Team

Can:

* create requests
* upload files
* review deliverables

---

## Graphics Team

Can:

* manage requests
* upload deliverables
* update statuses

---

## Admin

Can:

* manage users
* monitor workflow
* view analytics

---

# Frontend Pages

# Australia Team

```text
Dashboard
Create Request
My Requests
Completed Requests
```

---

# Graphics Team

```text
Assigned Tasks
In Progress Tasks
Completed Tasks
Upload Deliverables
```

---

# Admin Panel

```text
Users Management
Analytics
Request Monitoring
Performance Metrics
```

---

# MVP Scope (Phase 1)

## Included Features

* Login system
* Create request form
* File uploads
* Google Drive integration
* Dashboard
* Status management
* Final deliverable uploads
* Request tracking

---

# Excluded From MVP

These features will be implemented later:

* Real-time chat
* AI caption generation
* Analytics dashboard
* Mobile application
* Canva integrations
* Social media publishing
* Automated notifications
* Advanced permissions

---

# Recommended Development Timeline

# Day 1

* Backend setup
* Authentication
* Database schema

---

# Day 2

* Frontend UI
* Request creation forms
* Dashboard setup

---

# Day 3

* Google Drive integration
* File upload system

---

# Day 4

* Graphics team workflow
* Status management
* Deliverables module

---

# Day 5

* Testing
* UI polishing
* Bug fixing

---

# Estimated MVP Completion Time

## 5–7 Days

for a usable internal production MVP.

---

# Future Enhancements

# Phase 2

* Comments system
* Revision tracking
* Notifications
* Approval workflow
* File previews

---

# Phase 3

* AI-based caption generation
* Canva integrations
* Social media publishing
* Analytics dashboard
* Employee performance tracking

---

# Recommended Deployment

## Frontend

* Vercel

## Backend

* Render / AWS EC2

## Database

* MongoDB Atlas

---

# Expected Benefits

* Structured communication
* Faster turnaround time
* Centralized workflow
* Easier file management
* Better collaboration
* Reduced dependency on WhatsApp
* Improved operational efficiency

---

# Conclusion

The Internal Creative Request Management System will:

* replace unstructured communication
* centralize creative workflows
* improve coordination between teams
* streamline content production

The recommended approach is:

* React frontend
* Node.js backend
* MongoDB database
* Google Drive for storage
* Google Workspace authentication

This approach enables:

* rapid development
* easy scalability
* minimal operational disruption
* long-term maintainability
