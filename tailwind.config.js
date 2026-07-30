/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        paper: {
          DEFAULT: '#f5f6f9',
          2: '#ecedf2',
          3: '#e4e6ed',
        },
        ink: {
          DEFAULT: '#272a33',
          2: '#5c6170',
          muted: '#7a7f8e',
        },
        accent: {
          DEFAULT: '#1f3a64',
          2: '#2d4f82',
          light: '#e8edf5',
        },
        rule: '#d3d6e0',
      },
      fontFamily: {
        display: ['"DM Serif Display"', 'Georgia', 'serif'],
        body: ['"Geist"', 'system-ui', 'sans-serif'],
        mono: ['"Geist Mono"', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        'display': ['clamp(1.75rem, 4vw, 2.25rem)', { lineHeight: '1.15', fontWeight: '400' }],
      },
      borderRadius: {
        'card': '0.625rem',
      },
    },
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: [{
      dishub: {
        "primary": "#1f3a64",
        "primary-content": "#ffffff",
        "secondary": "#2d4f82",
        "secondary-content": "#ffffff",
        "accent": "#1f3a64",
        "accent-content": "#ffffff",
        "neutral": "#272a33",
        "neutral-content": "#f5f6f9",
        "base-100": "#f5f6f9",
        "base-200": "#ecedf2",
        "base-300": "#d3d6e0",
        "base-content": "#272a33",
        "info": "#2d4f82",
        "info-content": "#ffffff",
        "success": "#16a34a",
        "success-content": "#ffffff",
        "warning": "#d97706",
        "warning-content": "#ffffff",
        "error": "#dc2626",
        "error-content": "#ffffff",
        "--rounded-box": "0.625rem",
        "--rounded-btn": "0.375rem",
        "--rounded-badge": "9999px",
        "--animation-btn": "0.15s",
        "--animation-input": "0.15s",
        "--btn-focus-scale": "1",
      }
    }],
    logs: false,
  },
}
