# Workshop Management System

## Overview
This is a Flask-based Workshop Management System designed to track mechanical units through their service lifecycle. The application connects three departments: Traffic Control, Workshop, and Warehouse, allowing them to coordinate the workflow of mechanical units requiring maintenance or repair.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture
The system follows a traditional monolithic MVC (Model-View-Controller) architecture using Flask as the web framework:

1. **Backend**: Flask application with SQLAlchemy ORM
2. **Database**: SQLite for development, with configuration ready for PostgreSQL in production
3. **Frontend**: Jinja2 templates with Bootstrap 5 styling
4. **Authentication**: Flask-Login for user session management

The application supports multi-role access with different views and permissions based on department (Traffic Control, Workshop, Warehouse, and Admin).

## Key Components

### Models (models.py)
- **User**: Represents system users with department-based roles
- **Unit**: Represents a mechanical unit in the workshop system
- **StatusChange**: Tracks workflow changes for units
- **PartRequest**: Manages parts ordering/fulfillment

### Routes (routes.py)
Routes are organized by department/functionality:
- **Authentication**: Login/logout functionality
- **Traffic Control**: Unit registration and completion confirmation
- **Workshop**: Maintenance tracking and parts requests
- **Warehouse**: Parts management and fulfillment
- **Admin**: User management and system overview

### Forms (forms.py)
Form classes using Flask-WTF:
- **LoginForm**: User authentication
- **RegisterUnitForm**: Create new maintenance units
- **UpdateStatusForm**: Change unit status
- **PartRequestForm**: Request parts
- **UpdatePartRequestForm**: Update part request status
- **UserForm**: User management (admin)

### Templates
Organized by department with a shared base layout:
- **Base layout**: Navigation, styling, and common elements
- **Department-specific dashboards**: Traffic Control, Workshop, Warehouse
- **Functionality-specific pages**: Unit registration, part management, etc.

## Data Flow

1. **Unit Registration**:
   - Traffic Control registers a new unit → Unit status "registered"
   - Workshop picks up unit for service → Unit status "in_workshop"

2. **Parts Management**:
   - Workshop requests parts → Unit status "waiting_parts"
   - Warehouse fulfills part requests → Part status "available"
   - Workshop installs parts → Part status "installed"

3. **Unit Completion**:
   - Workshop completes maintenance → Unit status "completed"
   - Traffic Control confirms completion

## External Dependencies

### Python Packages
- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM for database interactions
- **Flask-Login**: User authentication
- **Flask-WTF**: Form handling and validation
- **WTForms**: Form creation and validation
- **Werkzeug**: Utilities including security handling
- **SQLAlchemy**: Database toolkit
- **Gunicorn**: WSGI HTTP server for deployment
- **Psycopg2**: PostgreSQL adapter

### Frontend Libraries
- **Bootstrap**: UI framework (loaded via CDN)
- **Font Awesome**: Icons (loaded via CDN)
- **DataTables**: Table enhancements (loaded via CDN)

## Deployment Strategy

The application is configured to run on Replit with:
- **WSGI Server**: Gunicorn serving the Flask application
- **Database**: Configuration ready for PostgreSQL (currently defaulting to SQLite)
- **Environment Variables**:
  - `SESSION_SECRET`: Secret key for session management
  - `DATABASE_URL`: Connection string for database

The deployment configuration is specified in the `.replit` file with autoscaling enabled for production deployment, binding to port 5000.

## Database Schema

The database consists of several related tables:
- **User**: ID, username, email, password_hash, department
- **Unit**: ID, unit_number, description, operator_name, current_status, registered_by_id
- **StatusChange**: ID, unit_id, user_id, previous_status, new_status, timestamp, notes
- **PartRequest**: ID, unit_id, user_id, part_name, quantity, status, timestamp, notes

## Development Workflow

1. Run the application locally: `python main.py`
2. For production: `gunicorn --bind 0.0.0.0:5000 main:app`

The application includes a workflow configuration for the Replit "Run" button, which will start the application with Gunicorn.