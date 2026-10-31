// Tailwind config for The Other Details research section (public/research/).
// House palette and Fontshare type from the lab's visual storytelling rules.
module.exports = {
  content: ["./src/research/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        ink: "#0b0c10", paper: "#f3efe6", muted: "#9a958b", dim: "#5f5c56",
        samba: "#a2242f", red: "#e0505c", teal: "#7fe3d6", gold: "#f4b942",
        edge: "rgba(255,255,255,.11)", glass: "rgba(255,255,255,.045)",
      },
      fontFamily: {
        head: ["Satoshi", "General Sans", "system-ui", "sans-serif"],
        ital: ["Gambetta", "Georgia", "serif"],
        body: ["General Sans", "system-ui", "sans-serif"],
      },
      maxWidth: { page: "1180px" },
    },
  },
};
