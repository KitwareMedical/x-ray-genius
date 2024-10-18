module.exports = {
    content: [
      './xray_genius/*/templates/**/*.html',
    ],
    safelist: [
      // Injected by Django, and may be referenced by CSS rules
      'errorlist',
    ],
    theme: {
      fontFamily: {
        'sans': 'Roboto, sans-serif',
      },
    },
    plugins: [
      require('@tailwindcss/typography'),
      require('daisyui'),
    ],
    daisyui: {
      themes: [
        {
          xrg_dark: {
            "primary": "#0D9488",
            "primary-content":  "#99F6E4",
            "neutral": "#3F3F46",
            "base-100": "#27272A",
            "base-200": "#3F3F46",
            "base-300": "#71717A",
            "info": "#93C5FD",
            "success": "#86EFAC",
            "warning": "#F59E0B",
            "error": "#F87171",
          },
        },
      ],
      logs: false,
    },
  }
