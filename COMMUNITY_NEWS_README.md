# Community News & Updates Management

## Overview
The Community News & Updates feature allows superusers to manage news items that are displayed to all users on their home pages and dashboards.

## Features

### For Superusers:
1. **Create News Items** - Add new community news with title, content, and active status
2. **Edit News Items** - Modify existing news items
3. **Delete News Items** - Remove news items from the system
4. **Toggle Active Status** - Quickly activate/deactivate news items
5. **View All News** - See all news items in a table format with statistics

### For All Users:
1. **View Active News** - See active news items on home pages and dashboards
2. **Real-time Updates** - News changes are immediately reflected across the platform

## Access Points

### Superuser Access:
- **Admin Dashboard**: Click "Manage News" in the Community News Management section
- **Direct URL**: `/farmcom/community-news/`
- **Create New**: `/farmcom/community-news/create/`

### User Access:
- **Logged-in Home Page**: News appears in the Community News & Updates section
- **All Dashboards**: News appears in the Community News & Updates section

## Sample News Items

The system comes with three sample news items:
1. **FarmCom Launches New Dashboard!** - Monitor your progress and team with our new dashboards.
2. **Upcoming Community Event** - Join us for the annual FarmCom networking event this August.
3. **Tips for Sustainable Farming** - Check out our latest blog post on sustainable agriculture practices.

## Technical Details

### Models:
- `CommunityNews` - Stores news items with title, content, timestamps, and active status

### Views:
- `community_news_list` - Display all news items
- `community_news_create` - Create new news items
- `community_news_edit` - Edit existing news items
- `community_news_delete` - Delete news items
- `community_news_toggle_active` - Toggle active status via AJAX

### Templates:
- `templates/farmcom/community_news_list.html` - News management interface
- `templates/farmcom/community_news_form.html` - Create/edit form
- `templates/farmcom/community_news_confirm_delete.html` - Delete confirmation

### URLs:
- All news management URLs are under `/farmcom/community-news/`
- Only accessible to superusers

## Usage Instructions

### Creating News:
1. Go to Admin Dashboard
2. Click "Manage News" in Community News Management section
3. Click "Create New News Item"
4. Fill in title and content
5. Check "Active" if you want it visible to users
6. Click "Save News Item"

### Editing News:
1. Go to News Management page
2. Click the edit icon (pencil) next to any news item
3. Make your changes
4. Click "Save News Item"

### Deleting News:
1. Go to News Management page
2. Click the delete icon (trash) next to any news item
3. Confirm deletion

### Toggling Active Status:
1. Go to News Management page
2. Click the eye icon next to any news item
3. Status will toggle immediately

## Security
- Only superusers can access news management
- All actions are logged for audit purposes
- CSRF protection enabled on all forms
- AJAX requests are properly secured

## Future Enhancements
- News categories/tags
- Scheduled publishing
- Rich text editor for content
- News images/attachments
- Email notifications for new news
- News analytics and engagement tracking 