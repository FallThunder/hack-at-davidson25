import type { Config } from 'tailwindcss';

export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],

	theme: {
		extend: {
			colors: {
				thepink: '#F0D6B5'
			}
		}
	},

	plugins: []
} satisfies Config;
