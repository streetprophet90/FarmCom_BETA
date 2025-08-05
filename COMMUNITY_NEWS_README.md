# Community News & Updates Management

## Overview
The Community News & Updates feature allows superusers to manage news items that are displayed to all users on their home pages and dashboards. This system has been enhanced with a comprehensive notification system for better user engagement.

## Features

### For Superusers:
1. **Create News Items** - Add new community news with title, content, and active status
2. **Edit News Items** - Modify existing news items
3. **Delete News Items** - Remove news items from the system
4. **Toggle Active Status** - Quickly activate/deactivate news items
5. **View All News** - See all news items in a table format with statistics
6. **Enhanced Notifications** - Send notifications to users when news is published

### For All Users:
1. **View Active News** - See active news items on home pages and dashboards
2. **Real-time Updates** - News changes are immediately reflected across the platform
3. **Notification Preferences** - Customize how and when to receive notifications
4. **Enhanced Notification System** - Real-time alerts with sound, badges, and email options

## Enhanced Notification System

### User Notification Preferences:
- **Email Notifications**: Receive news updates via email
- **Push Notifications**: Browser-based real-time alerts
- **Notification Sound**: Audio alerts for new notifications
- **Notification Frequency**: Choose between immediate, hourly, daily, or weekly digests

### Notification Types:
- **News Published**: When new community news is published
- **News Updated**: When existing news is modified
- **System Alerts**: Platform-wide announcements
- **Forum Notifications**: Topic requests and responses
- **Permission Updates**: Changes to user permissions

## Access Points

### Superuser Access:
- **Admin Dashboard**: Click "Manage News" in the Community News Management section
- **Direct URL**: `/farmcom/community-news/`
- **Create New**: `/farmcom/community-news/create/`
- **Notification Settings**: `/accounts/notification-settings/`

### User Access:
- **Logged-in Home Page**: News appears in the Community News & Updates section
- **All Dashboards**: News appears in the Community News & Updates section
- **Notification Center**: `/accounts/notifications/` for managing all notifications
- **Notification Settings**: `/accounts/notification-settings/` for preferences

## Sample News Items

The system comes with three sample news items:
1. **FarmCom Launches New Dashboard!** - Monitor your progress and team with our new dashboards.
2. **Upcoming Community Event** - Join us for the annual FarmCom networking event this August.
3. **Tips for Sustainable Farming** - Check out our latest blog post on sustainable agriculture practices.

## Technical Details

### Models:
- `CommunityNews` - Stores news items with title, content, timestamps, and active status
- `Notification` - Enhanced notification system with user preferences
- `User` - Extended with notification preference fields

### Views:
- `community_news_list` - Display all news items
- `community_news_create` - Create new news items
- `community_news_edit` - Edit existing news items
- `community_news_delete` - Delete news items
- `community_news_toggle_active` - Toggle active status via AJAX
- `notification_settings` - Manage user notification preferences
- `update_notification_settings` - Update notification preferences via AJAX
- `test_notification` - Test notification system

### Templates:
- `templates/farmcom/community_news_list.html` - News management interface
- `templates/farmcom/community_news_form.html` - Create/edit form
- `templates/farmcom/community_news_confirm_delete.html` - Delete confirmation
- `templates/accounts/notification_settings.html` - Notification preferences
- `templates/accounts/notifications.html` - Notification center

### URLs:
- All news management URLs are under `/farmcom/community-news/`
- Notification URLs are under `/accounts/notifications/`
- Only accessible to superusers for news management

## Usage Instructions

### Creating News:
1. Go to Admin Dashboard
2. Click "Manage News" in Community News Management section
3. Click "Create New News Item"
4. Fill in title and content
5. Check "Active" if you want it visible to users
6. Click "Save News Item"
7. Users will receive notifications based on their preferences

### Managing Notifications:
1. Go to Notification Settings (`/accounts/notification-settings/`)
2. Configure email, push, and sound preferences
3. Set notification frequency (immediate, hourly, daily, weekly)
4. Test notifications using the "Test Notification" button
5. View all notifications in the Notification Center

### Editing News:
1. Go to News Management page
2. Click the edit icon (pencil) next to any news item
3. Make your changes
4. Click "Save News Item"
5. Users will be notified of updates

### Deleting News:
1. Go to News Management page
2. Click the delete icon (trash) next to any news item
3. Confirm deletion

### Toggling Active Status:
1. Go to News Management page
2. Click the eye icon next to any news item
3. Status will toggle immediately

## Enhanced Notification Features

### Real-time Updates:
- AJAX-powered notification updates
- Live notification badges
- Sound alerts for new notifications
- Email notifications for important updates

### User Control:
- Customizable notification preferences
- Frequency control (immediate to weekly)
- Sound toggle for audio alerts
- Email and push notification toggles

### Admin Features:
- Test notification system
- Monitor notification delivery
- Track user engagement with notifications

## Security
- Only superusers can access news management
- All actions are logged for audit purposes
- CSRF protection enabled on all forms
- AJAX requests are properly secured
- Notification preferences are user-specific and secure

## Future Enhancements
- News categories/tags
- Scheduled publishing
- Rich text editor for content
- News images/attachments
- Advanced notification analytics
- Notification engagement tracking
- Mobile push notifications
- Notification templates for different news types

## Recent Updates (July 19, 2025)
- ✅ Enhanced notification system with user preferences
- ✅ Real-time notification updates via AJAX
- ✅ Notification sound and badge features
- ✅ Email notification integration
- ✅ Notification frequency controls
- ✅ Test notification functionality
- ✅ Notification center with management interface 