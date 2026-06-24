import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { Button } from "@/components/ui/button";
import { Navbar } from "@/components/landing/navbar";
import { Footer } from "@/components/landing/footer";
import {
  ShieldCheck,
  Layers,
  Globe,
  Zap,
  Lock,
  Smartphone,
} from "lucide-react";

export default async function LandingPage() {
  const t = await getTranslations("Landing");

  const features = [
    {
      icon: Lock,
      title: t("features.auth.title"),
      desc: t("features.auth.desc"),
    },
    {
      icon: Globe,
      title: t("features.i18n.title"),
      desc: t("features.i18n.desc"),
    },
    {
      icon: Zap,
      title: t("features.fast.title"),
      desc: t("features.fast.desc"),
    },
    {
      icon: Smartphone,
      title: t("features.mobile.title"),
      desc: t("features.mobile.desc"),
    },
    {
      icon: ShieldCheck,
      title: t("features.secure.title"),
      desc: t("features.secure.desc"),
    },
    {
      icon: Layers,
      title: t("features.scalable.title"),
      desc: t("features.scalable.desc"),
    },
  ];

  const stack = [
    { name: "Next.js 16", tag: "Framework" },
    { name: "TypeScript", tag: "Language" },
    { name: "Tailwind v4", tag: "Styling" },
    { name: "shadcn/ui", tag: "Components" },
    { name: "Neon", tag: "Postgres" },
    { name: "Vercel", tag: "Deploy" },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      {/* Hero — asymmetric, left-aligned */}
      <section className="relative overflow-hidden pt-32 pb-20 sm:pt-40 sm:pb-28">
        {/* Subtle grid background */}
        <div
          className="absolute inset-0 -z-10 opacity-[0.035]"
          style={{
            backgroundImage:
              "linear-gradient(to right, var(--foreground) 1px, transparent 1px), linear-gradient(to bottom, var(--foreground) 1px, transparent 1px)",
            backgroundSize: "64px 64px",
          }}
        />

        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <div className="grid items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
            {/* Left: copy */}
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs text-muted-foreground">
                <span className="size-1.5 rounded-full bg-emerald-500" />
                {t("hero.badge")}
              </div>
              <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
                {t("hero.title")}
              </h1>
              <p className="max-w-xl text-lg text-muted-foreground sm:text-xl">
                {t("hero.subtitle")}
              </p>
              <div className="flex flex-wrap items-center gap-3 pt-2">
                <Link href="/signup">
                  <Button size="lg" className="h-11 px-6 text-base">
                    {t("hero.ctaPrimary")}
                  </Button>
                </Link>
                <a href="#features">
                  <Button
                    variant="outline"
                    size="lg"
                    className="h-11 px-6 text-base"
                  >
                    {t("hero.ctaSecondary")}
                  </Button>
                </a>
              </div>
            </div>

            {/* Right: app mockup */}
            <div className="hidden lg:block">
              <div className="rounded-xl border bg-card p-2 shadow-sm">
                {/* Window bar */}
                <div className="flex items-center gap-1.5 px-2 py-2">
                  <div className="size-2.5 rounded-full bg-muted-foreground/20" />
                  <div className="size-2.5 rounded-full bg-muted-foreground/20" />
                  <div className="size-2.5 rounded-full bg-muted-foreground/20" />
                </div>
                {/* App content mockup */}
                <div className="space-y-3 rounded-lg border bg-background p-4">
                  {/* Sidebar + main */}
                  <div className="flex gap-4">
                    <div className="w-28 space-y-2">
                      <div className="h-3 w-20 rounded bg-muted-foreground/15" />
                      <div className="space-y-1.5 pt-2">
                        <div className="h-2.5 w-full rounded bg-muted-foreground/10" />
                        <div className="h-2.5 w-3/4 rounded bg-muted-foreground/10" />
                        <div className="h-2.5 w-5/6 rounded bg-muted-foreground/10" />
                      </div>
                    </div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 w-32 rounded bg-muted-foreground/20" />
                      <div className="grid grid-cols-3 gap-2 pt-1">
                        <div className="h-16 rounded-lg border bg-muted/40" />
                        <div className="h-16 rounded-lg border bg-muted/40" />
                        <div className="h-16 rounded-lg border bg-muted/40" />
                      </div>
                      <div className="h-20 rounded-lg border bg-muted/30" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section className="border-y">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <div className="grid grid-cols-2 divide-x md:grid-cols-4">
            {[
              { value: "16", label: t("stats.next") },
              { value: "2", label: t("stats.locales") },
              { value: "10+", label: t("stats.components") },
              { value: "~2min", label: t("stats.deploy") },
            ].map((stat, i) => (
              <div
                key={i}
                className="px-4 py-8 text-center first:border-l-0"
              >
                <p className="text-2xl font-bold tracking-tight sm:text-3xl">
                  {stat.value}
                </p>
                <p className="mt-1 text-xs text-muted-foreground sm:text-sm">
                  {stat.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features — asymmetric grid */}
      <section id="features" className="py-20 sm:py-28">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <div className="max-w-2xl">
            <p className="text-sm font-medium text-muted-foreground">
              {t("features.label")}
            </p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
              {t("features.title")}
            </h2>
            <p className="mt-3 text-muted-foreground">
              {t("features.subtitle")}
            </p>
          </div>

          <div className="mt-12 grid gap-px overflow-hidden rounded-xl border bg-border sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="bg-background p-6 transition-colors hover:bg-muted/30"
              >
                <div className="flex size-10 items-center justify-center rounded-lg border">
                  <feature.icon className="size-5 text-muted-foreground" />
                </div>
                <h3 className="mt-4 text-base font-semibold">
                  {feature.title}
                </h3>
                <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech stack section */}
      <section id="stack" className="border-t bg-muted/20 py-20 sm:py-28">
        <div className="mx-auto max-w-6xl px-4 sm:px-6">
          <div className="grid gap-12 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                {t("stack.label")}
              </p>
              <h2 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
                {t("stack.title")}
              </h2>
              <p className="mt-3 text-muted-foreground">
                {t("stack.subtitle")}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {stack.map((tech) => (
                <div
                  key={tech.name}
                  className="rounded-lg border bg-background p-4"
                >
                  <p className="text-xs text-muted-foreground">{tech.tag}</p>
                  <p className="mt-1 text-sm font-semibold">{tech.name}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section id="cta" className="py-20 sm:py-28">
        <div className="mx-auto max-w-3xl px-4 text-center sm:px-6">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            {t("cta.title")}
          </h2>
          <p className="mt-3 text-muted-foreground">
            {t("cta.subtitle")}
          </p>
          <div className="mt-8 flex items-center justify-center gap-3">
            <Link href="/signup">
              <Button size="lg" className="h-11 px-8 text-base">
                {t("cta.primary")}
              </Button>
            </Link>
            <Link href="/login">
              <Button
                variant="outline"
                size="lg"
                className="h-11 px-8 text-base"
              >
                {t("cta.secondary")}
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
