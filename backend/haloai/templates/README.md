# Halo AI Template Structure Documentation

## Overview

The templates have been completely refactored to use modern, professional structure with Tailwind CSS for styling. This documentation outlines the new organization and usage patterns.

## Directory Structure

```
templates/
├── base.html                 # Base template with common layout
├── home/
│   └── index.html           # Homepage
├── users/
│   ├── login.html           # User login page
│   └── signup.html          # User registration page
├── crops/
│   └── prediction.html      # Crop recommendation form
├── dashboard/
│   └── index.html          # User dashboard
├── community/
│   └── contact.html        # Contact page
├── analytics/              # Analytics templates
├── sensors/               # Sensor management templates
└── grants/                # Grants and offers templates
```

## Key Features

### 1. Base Template (`base.html`)

- **Tailwind CSS Integration**: Full Tailwind CSS setup with custom color palette
- **Responsive Navigation**: Mobile-friendly navigation with hamburger menu
- **Custom Color Scheme**:
  - Primary: Green shades for agriculture theme
  - Secondary: Amber/yellow shades for warmth
- **Blocks Available**:
  - `title`: Page title
  - `extra_css`: Additional CSS
  - `navigation`: Override navigation
  - `main_class`: Main content classes
  - `content`: Main page content
  - `footer`: Override footer
  - `extra_js`: Additional JavaScript

### 2. Homepage (`home/index.html`)

- **Modern Hero Section**: Gradient background with compelling copy
- **Features Grid**: Three-column layout showcasing key features
- **Statistics Section**: Impressive numbers to build trust
- **Call-to-Action**: Prominent signup encouragement
- **Responsive Design**: Mobile-first approach

### 3. Authentication Templates

#### Login (`users/login.html`)

- **Clean Form Design**: Focused single-column layout
- **Password Toggle**: Show/hide password functionality
- **Social Login**: Ready for Google/Facebook integration
- **Remember Me**: Checkbox for persistent sessions
- **Responsive**: Works on all screen sizes

#### Signup (`users/signup.html`)

- **Comprehensive Form**: All necessary user information
- **Password Confirmation**: Client-side validation
- **Terms Agreement**: Legal compliance checkboxes
- **Newsletter Opt-in**: Marketing permission
- **Progressive Enhancement**: Works without JavaScript

### 4. Crop Prediction (`crops/prediction.html`)

- **Multi-section Form**: Organized into soil, climate, and farm sections
- **Sample Data**: Quick-fill functionality for testing
- **Real-time Validation**: Immediate feedback on inputs
- **Results Modal**: In-page results display
- **Help Resources**: Side panel with tips and guidance

### 5. Dashboard (`dashboard/index.html`)

- **Statistics Cards**: Key metrics at a glance
- **Recent Activity**: Timeline of user actions
- **Weather Widget**: Current conditions and forecast
- **Quick Actions**: Common tasks easily accessible
- **Responsive Grid**: Adapts to screen size

### 6. Contact Page (`community/contact.html`)

- **Contact Form**: Comprehensive inquiry form
- **Contact Information**: Multiple ways to reach support
- **FAQ Links**: Quick help resources
- **Social Media**: Links to social platforms
- **Interactive Elements**: Form validation and submission feedback

## Technical Implementation

### Tailwind CSS Configuration

```javascript
tailwind.config = {
  theme: {
    extend: {
      colors: {
        primary: {
          // Green palette for agriculture
          50: "#f0fdf4",
          500: "#22c55e",
          600: "#16a34a",
          // ... full range
        },
        secondary: {
          // Amber palette for warmth
          50: "#fefce8",
          500: "#f59e0b",
          600: "#d97706",
          // ... full range
        },
      },
      fontFamily: {
        manrope: ["Manrope", "sans-serif"],
      },
    },
  },
};
```

### JavaScript Functionality (`static/js/main.js`)

- **Mobile Menu**: Toggle functionality for responsive navigation
- **Form Validation**: Client-side validation helpers
- **Notifications**: Toast notification system
- **Loading States**: Button loading animations
- **Utility Functions**: Debouncing, formatting, etc.

## Usage Guidelines

### 1. Creating New Templates

```django
{% extends 'base.html' %}
{% load static %}

{% block title %}Your Page Title - Halo AI{% endblock %}

{% block content %}
<!-- Your content here -->
{% endblock %}
```

### 2. Adding Custom Styles

```django
{% block extra_css %}
<style>
  /* Custom styles for this page */
</style>
{% endblock %}
```

### 3. Adding Custom JavaScript

```django
{% block extra_js %}
<script>
  // Custom JavaScript for this page
</script>
{% endblock %}
```

### 4. URL Patterns

Ensure your URL patterns follow the namespace convention:

```python
# In app/urls.py
app_name = "your_app"
urlpatterns = [
    path('', views.index, name='index'),
    path('detail/', views.detail, name='detail'),
]

# In templates, use:
{% url 'your_app:index' %}
```

## Color Palette Usage

### Primary Colors (Green - Agriculture)

- `bg-primary-50`: Very light backgrounds
- `bg-primary-100`: Light accent backgrounds
- `bg-primary-600`: Main brand color
- `text-primary-600`: Brand text color
- `border-primary-500`: Form focus states

### Secondary Colors (Amber - Energy)

- `bg-secondary-50`: Warm light backgrounds
- `bg-secondary-600`: Call-to-action buttons
- `text-secondary-600`: Accent text

### Utility Colors

- `bg-gray-50`: Page backgrounds
- `bg-white`: Card backgrounds
- `text-gray-900`: Primary text
- `text-gray-600`: Secondary text
- `text-gray-400`: Placeholder text

## Responsive Breakpoints

- **Mobile**: Default (< 768px)
- **Tablet**: `md:` (768px+)
- **Desktop**: `lg:` (1024px+)
- **Large**: `xl:` (1280px+)

## Best Practices

1. **Mobile First**: Design for mobile, enhance for desktop
2. **Semantic HTML**: Use proper HTML5 semantic elements
3. **Accessibility**: Include ARIA labels and keyboard navigation
4. **Performance**: Optimize images and minimize CSS/JS
5. **SEO**: Use proper meta tags and structured data
6. **Progressive Enhancement**: Ensure functionality without JavaScript

## Migration Notes

### From Old Structure

- Old mixed templates have been reorganized by feature
- CSS has been converted from custom files to Tailwind classes
- JavaScript has been consolidated into `main.js`
- URL patterns updated to use namespaces

### Breaking Changes

- Template paths have changed (use new directory structure)
- CSS classes replaced with Tailwind utilities
- Some JavaScript functions renamed for consistency

## Future Enhancements

1. **Component System**: Create reusable template components
2. **Theme Switching**: Dark/light mode toggle
3. **Internationalization**: Multi-language support
4. **Advanced Animations**: Micro-interactions and transitions
5. **PWA Features**: Service worker and offline functionality

## Support

For questions about the template structure or implementation, refer to:

- Django Template Documentation
- Tailwind CSS Documentation
- This documentation file

Last updated: June 25, 2025
