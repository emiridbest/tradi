"use client";

import { useState } from "react";
import { useTheme } from "next-themes";
import { useColorTheme, themeOptions } from "./ThemeProvider";
import { Check, Moon, Palette, Sun } from "lucide-react";
import { Button } from "./ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "./ui/dropdown-menu";

export function ThemeSelector() {
  const { theme, setTheme } = useTheme();
  const { colorTheme, applyTheme } = useColorTheme();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>
          <Sun className="mr-2 h-4 w-4" />
          <span>Light</span>
          {theme === "light" && <Check className="ml-auto h-4 w-4" />}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>
          <Moon className="mr-2 h-4 w-4" />
          <span>Dark</span>
          {theme === "dark" && <Check className="ml-auto h-4 w-4" />}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>
          <Palette className="mr-2 h-4 w-4" />
          <span>System</span>
          {theme === "system" && <Check className="ml-auto h-4 w-4" />}
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        {Object.keys(themeOptions).map((key) => (
          <DropdownMenuItem 
            key={key}
            onClick={() => applyTheme(key)}
            className="flex items-center"
          >
            <div 
              className="w-4 h-4 mr-2 rounded-full" 
              style={{ 
                background: `linear-gradient(135deg, 
                  ${themeOptions[key as keyof typeof themeOptions].primary}, 
                  ${themeOptions[key as keyof typeof themeOptions].secondary})` 
              }} 
            />
            <span>{themeOptions[key as keyof typeof themeOptions].name}</span>
            {colorTheme === key && <Check className="ml-auto h-4 w-4" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}