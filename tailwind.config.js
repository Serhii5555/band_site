/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/**/*.html", "./app/static/**/*.js"],
  theme: {
    extend: {},
  },
  plugins: [],
  theme: {
    screens: {
      xs: "400px",
    },
  },
};
