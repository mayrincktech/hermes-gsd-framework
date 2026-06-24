"use client";

import { useState, useEffect } from "react";
import { Link } from "@/i18n/navigation";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { LanguageSwitcher } from "@/components/layout/language-switcher";
import { cn } from "@/lib/utils";

export function Navbar() {
  const t = useTranslations("Landing");
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "fixed inset-x-0 top-0 z-50 transition-all duration-200",
        scrolled
          ? "border-b bg-background/80 backdrop-blur-md"
          : "border-b border-transparent"
      )}
    >
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <div className="size-7 rounded-md bg-foreground" />
          <span className="text-base font-semibold tracking-tight">
            App Name
          </span>
        </Link>

        {/* Center nav (desktop) */}
        <nav className="hidden items-center gap-8 md:flex">
          <Link
            href="/"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            {t("nav.features")}
          </Link>
          <a
            href="#stack"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            {t("nav.stack")}
          </a>
          <a
            href="#cta"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            {t("nav.pricing")}
          </a>
        </nav>

        {/* Right actions */}
        <div className="flex items-center gap-2">
          <LanguageSwitcher />
          <ThemeToggle />
          <div className="hidden items-center gap-2 sm:flex">
            <Link href="/login">
              <Button variant="ghost" size="sm">
                {t("nav.signIn")}
              </Button>
            </Link>
            <Link href="/signup">
              <Button size="sm">
                {t("nav.getStarted")}
              </Button>
            </Link>
          </div>
          {/* Mobile: just sign in icon */}
          <Link href="/login" className="sm:hidden">
            <Button variant="ghost" size="sm">
              {t("nav.signIn")}
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
}
