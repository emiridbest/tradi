"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import { type ThemeProviderProps } from "next-themes";

// Define additional theme configurations
export const themeOptions = {
  default: {
    name: "Default",
    primary: "hsl(196, 94%, 48%)",
    secondary: "hsl(291, 84%, 61%)",
    accent: "hsl(262, 83%, 64%)",
  },
  vibrant: {
    name: "Vibrant",
    primary: "hsl(196, 100%, 50%)",
    secondary: "hsl(320, 100%, 60%)",
    accent: "hsl(262, 100%, 68%)",
  },
  neon: {
    name: "Neon",
    primary: "hsl(150, 100%, 50%)",
    secondary: "hsl(280, 100%, 65%)",
    accent: "hsl(320, 100%, 55%)",
  },
  sunset: {
    name: "Sunset",
    primary: "hsl(25, 100%, 55%)",
    secondary: "hsl(320, 100%, 60%)",
    accent: "hsl(280, 90%, 60%)",
  },
};

// Create context for additional theme options
type ColorThemeContextType = {
  colorTheme: string;
  setColorTheme: (theme: string) => void;
  applyTheme: (theme: string) => void;
};

const ColorThemeContext = createContext<ColorThemeContextType>({
  colorTheme: "default",
  setColorTheme: () => null,
  applyTheme: () => null,
});

export const useColorTheme = () => useContext(ColorThemeContext);

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  const [colorTheme, setColorTheme] = useState("default");

  // Function to apply CSS variables for the selected theme
  const applyTheme = (themeName: string) => {
    const theme = themeOptions[themeName as keyof typeof themeOptions] || themeOptions.default;
    
    document.documentElement.style.setProperty("--primary", theme.primary);
    document.documentElement.style.setProperty("--secondary", theme.secondary);
    document.documentElement.style.setProperty("--accent", theme.accent);
    
    // Store the preference
    localStorage.setItem("color-theme", themeName);
    setColorTheme(themeName);
  };

  // Initialize theme from localStorage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem("color-theme") || "default";
    applyTheme(savedTheme);
  }, []);

  return (
    <ColorThemeContext.Provider value={{ colorTheme, setColorTheme, applyTheme }}>
      <NextThemesProvider {...props}>{children}</NextThemesProvider>
    </ColorThemeContext.Provider>
  );
}