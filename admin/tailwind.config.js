/** @type {import('tailwindcss').Config} */

module.exports = {
	content: [
		'./index.html',
		'./src/**/*.{html,js,ts,vue}'
	],
	theme: {
		extend: {
			transitionProperty: {
				'height': 'height',
				'spacing': 'margin, padding',
				'width': 'width',
				'fadetransform': 'opacity, transform',
			},
			maxWidth: {
				'1/2': '50%',
			},
			minWidth: {
				'1/2': '50%',
			},
			aspectRatio: {
				'4/3': '4 / 3',
				'phone': '9 / 16',
			},
			borderRadius: {
				'4xl': '2rem',
			},
		},
	},
	plugins: [
		require('@tailwindcss/forms'),
		require('daisyui'),
	],
	darkMode: ['class', '[data-theme="dark"]'],
	daisyui: {
		themes: [
			{
				light: {
					"primary": "#383938",
					"secondary": "#633DCC",
					"accent": "#F3977B",
					"neutral": "#383938",
					"base-100": "#E9DDC6",
					"info": "#38BDF8",
					"success": "#22C55E",
					"warning": "#EAB308",
					"error": "#EF4444",
				},
			},
			{
				dark: {
					"primary": "#383938",
					"secondary": "#C27862",
					"accent": "#7C4DFF",
					"neutral": "#383938",
					"base-100": "#D4BC8F",
					"info": "#38BDF8",
					"success": "#22C55E",
					"warning": "#EAB308",
					"error": "#EF4444",
				},
			},
		],
	},
}

