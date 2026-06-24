import { Link } from "@/i18n/navigation";
import { useTranslations } from "next-intl";

export function Footer() {
  const t = useTranslations("Landing");

  return (
    <footer className="border-t">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <div className="flex flex-col items-start justify-between gap-8 md:flex-row">
          {/* Brand */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="size-6 rounded-md bg-foreground" />
              <span className="text-sm font-semibold">App Name</span>
            </div>
            <p className="max-w-xs text-sm text-muted-foreground">
              {t("footer.tagline")}
            </p>
          </div>

          {/* Links */}
          <div className="grid grid-cols-2 gap-8 sm:grid-cols-3">
            <div className="space-y-3">
              <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                {t("footer.product")}
              </p>
              <ul className="space-y-2">
                <li>
                  <a
                    href="#features"
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {t("nav.features")}
                  </a>
                </li>
                <li>
                  <a
                    href="#stack"
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {t("nav.stack")}
                  </a>
                </li>
                <li>
                  <Link
                    href="/signup"
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {t("nav.getStarted")}
                  </Link>
                </li>
              </ul>
            </div>

            <div className="space-y-3">
              <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                {t("footer.company")}
              </p>
              <ul className="space-y-2">
                <li>
                  <a
                    href="#"
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {t("footer.about")}
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {t("footer.contact")}
                  </a>
                </li>
              </ul>
            </div>

            <div className="space-y-3">
              <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                {t("footer.legal")}
              </p>
              <ul className="space-y-2">
                <li>
                  <a
                    href="#"
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {t("footer.privacy")}
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    {t("footer.terms")}
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-12 flex items-center justify-between border-t pt-6">
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} App Name. {t("footer.rights")}
          </p>
        </div>
      </div>
    </footer>
  );
}
