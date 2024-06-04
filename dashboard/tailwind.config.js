/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './src/**/*.{html,svelte,js,ts}',
    './node_modules/layerchart/**/*.{svelte,js}'
  ],
  theme: {
    extend: {},
  },
  plugins: [require('daisyui')],
}

