# YT2Spot Frontend

React-based web interface for the YouTube Music to Spotify migration tool.

## Overview

The frontend provides an intuitive web interface for migrating music libraries between platforms with real-time progress tracking and OAuth authentication.

## Features

- **Service Selection**: Choose between direct platform authentication or file upload
- **OAuth Integration**: Secure authentication with Spotify and YouTube Music
- **Real-time Migration**: Live progress visualization with animated updates
- **Responsive Design**: Mobile-friendly interface with Spotify-inspired styling
- **Interactive Decisions**: Manual resolution for ambiguous track matches

## Technology Stack

- **React 18**: Modern React with hooks and TypeScript
- **TypeScript**: Type-safe development with full type coverage
- **Vite**: Fast development server and optimized builds
- **Tailwind CSS**: Utility-first CSS framework for rapid styling
- **Lucide React**: Modern icon library for consistent iconography

## Development

### Prerequisites

- Node.js 16 or higher
- npm or yarn package manager

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Authentication.tsx
│   │   ├── LiveMigration.tsx
│   │   ├── ServiceSelector.tsx
│   │   └── ...
│   ├── utils/              # Utility functions
│   │   └── api.ts          # API client
│   ├── types.ts            # TypeScript type definitions
│   ├── App.tsx             # Main application component
│   └── main.tsx            # Application entry point
├── public/                 # Static assets
├── package.json            # Dependencies and scripts
└── vite.config.ts          # Vite configuration
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler check

### Development Server

The development server runs on `http://localhost:3000` by default and includes:
- Hot module replacement for instant updates
- TypeScript compilation with error reporting
- Automatic port switching if 3000 is occupied

### API Integration

The frontend communicates with the FastAPI backend running on `http://localhost:8000`. Key API endpoints:

- `POST /upload` - File upload for migration
- `GET /migrate/status/{id}` - Migration progress
- `GET /api/auth/spotify` - OAuth authentication
- `POST /migrate/decision` - User decisions

### Component Architecture

#### ServiceSelector
Handles platform selection (Spotify, YouTube Music, File Upload) with step-by-step flow.

#### Authentication
Manages OAuth flows with popup windows and secure token handling.

#### LiveMigration
Real-time migration dashboard with animated progress indicators and live updates.

#### MigrationProgress
File-based migration progress tracking with interactive decision making.

### Styling

The application uses Tailwind CSS with a custom Spotify-inspired color scheme:

```css
:root {
  --spotify-green: #1db954;
  --spotify-black: #191414;
  --spotify-dark: #121212;
  --spotify-gray: #b3b3b3;
}
```

### Type Safety

Full TypeScript coverage with strict type checking enabled. Key type definitions:

- `MigrationSession` - Migration state management
- `AuthenticationData` - OAuth authentication results
- `ServiceOption` - Platform service definitions

### Building for Production

```bash
npm run build
```

Builds the app for production to the `dist` folder with:
- Optimized React production build
- Minified and bundled JavaScript/CSS
- Static asset optimization
- Tree-shaking for minimal bundle size

## Configuration

### Environment Variables

Create a `.env.local` file for development:

```bash
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=YT2Spot
```

### Backend Integration

Ensure the backend server is running on port 8000 before starting the frontend development server.

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the existing code style and TypeScript patterns
2. Add proper type annotations for new components
3. Test components in both desktop and mobile viewports
4. Ensure accessibility compliance (ARIA labels, keyboard navigation)

## Performance

The frontend is optimized for performance with:
- Code splitting for reduced initial bundle size
- Lazy loading of non-critical components
- Efficient state management with React hooks
- Optimized re-renders with proper dependency arrays
