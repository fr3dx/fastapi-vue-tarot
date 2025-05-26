import { createI18n } from "vue-i18n";
import en from "./locales/en.json";
import hu from "./locales/hu.json";

const userLang = navigator.language?.startsWith("hu") ? "hu" : "en";

const i18n = createI18n({
  legacy: false, // Using Composition API
  locale: userLang,
  fallbackLocale: "en",
  messages: {
    en,
    hu,
  },
});

export default i18n;
