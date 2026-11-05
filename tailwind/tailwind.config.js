// Tailwind settings for Griot Fitness.
// Rebuild the CSS after adding or changing Tailwind classes in any template (run from the project folder):
//   npx tailwindcss@3.4.17 -c tailwind/tailwind.config.js -i tailwind/input.css -o app/static/css/tailwind.css --minify
module.exports = {
  // Tailwind scans these files and only keeps the classes they actually use
  content: ["./app/templates/**/*.html"],
  theme: {
    extend: {
      // The Griot palette, so classes like bg-panther / text-gold work everywhere
      colors: {
        panther: "#0D0D10",       // page background (60%)
        talokan: "#0A1F33",       // sidebar, cards, sections (30%)
        "talokan-2": "#0F2A45",   // inputs + hover on navy
        mourning: "#F2EFE9",      // main text
        muted: "#A9B4C2",         // secondary text (8:1 on navy)
        gold: "#C9A24A",          // primary - main buttons, links, key numbers (use sparingly)
        "gold-2": "#B08A36",
        vibranium: "#7B3FC4",     // accent - glows, borders, focus (not body text)
        "vib-light": "#B48BEA",   // readable purple tint for small text on navy
        teal: "#1F8A8A",          // secondary - tags, icons, secondary buttons
        "teal-light": "#5FC4C4",  // readable teal tint for small text on navy
        danger: "#A3192E"         // errors - only ever with light text on top
      },
      fontFamily: {
        head: ["Sora", "Segoe UI", "system-ui", "sans-serif"],
        body: ["Manrope", "Segoe UI", "system-ui", "sans-serif"]
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(123,63,196,.5), 0 10px 30px rgba(123,63,196,.25)",
        card: "0 12px 32px rgba(0,0,0,.35)"
      }
    }
  }
};
