// Copyright [2019] [Integreat Project]
// Copyright [2023] [YCMS]
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
const colors = require("tailwindcss/colors");

module.exports = {
  content: [
    "./hospitool/cms/templates/**/*.html",
    "./hospitool/static/src/js/**/*.{js,ts,tsx}",
    "./node_modules/flowbite/**/*.js",
  ],
  theme: {
    colors: {
      transparent: "transparent",
      current: "currentColor",
      black: colors.black,
      white: colors.white,
      gray: colors.slate,
      red: colors.red,
      orange: colors.orange,
      yellow: colors.yellow,
      green: colors.green,
      blue: colors.blue,
      violet: colors.violet,
      primary: "#FBDA16",
      secondary: "#334253",
      tertiary: "#E9E9E9",
    },
    extend: {
      colors: {
        water: {
          50: "#fefeff",
          100: "#fcfdff",
          200: "#f8fafe",
          300: "#f4f7fe",
          400: "#ecf1fd",
          500: "#e4ebfc",
          600: "#cdd4e3",
          700: "#abb0bd",
          800: "#898d97",
          900: "#70737b",
        },
        background: {
          50: "#fafafa",
          900: "#0a0011ab",
        },
      },
      backgroundImage: {
        "hospitool-icon": "url('../images/favicon.svg')",
        "hospitool-logo": "url('../images/logo-bed.svg')",
      },
      fontFamily: {
        "default": ["Roboto", "Raleway", "Lateef", "Noto Sans SC", "sans-serif", "Noto Sans Ethiopic"],
        "content": ["Open Sans", "sans-serif"],
        "content-rtl": ["Lateef", "sans-serif"],
        "content-sc": ["Noto Sans SC", "sans-serif"],
        "content-am": ["Noto Sans Ethiopic", "sans-serif"],
      },
      maxHeight: {
        15: "3.75rem",
        116: "29rem",
        160: "40rem",
      },
      gridTemplateColumns: {
        gallery: "repeat(auto-fill, minmax(180px, 1fr))",
      },
      width: {
        120: "30rem",
        136: "34rem",
        160: "40rem",
      },
      screens: {
        "3xl": "1700px",
        "4xl": "2100px",
      },
    },
  },
  darkMode: "class",
  plugins: [require("@tailwindcss/forms"), require("flowbite/plugin")],
};
