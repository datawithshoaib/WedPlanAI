"use client";

import { Heart, RefreshCw } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useHealth } from "@/components/health-provider";
import { RuntimeStatus } from "@/components/runtime-status";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  { href: "/", label: "New plan", match: (path: string) => path === "/" },
  { href: "/plans", label: "History", match: (path: string) => path.startsWith("/plans") },
];

export function SiteHeader() {
  const pathname = usePathname();
  const { health, loading, offline, refresh } = useHealth();

  return (
    <header className="sticky top-0 z-30 border-b bg-card/85 backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-x-4 gap-y-2 px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-3">
          <span className="flex size-9 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-chart-5 text-primary-foreground shadow-sm">
            <Heart className="size-4" aria-hidden />
          </span>
          <span>
            <span className="block font-heading text-xl leading-none font-bold">WedPlannerAI</span>
            <span className="hidden text-xs text-muted-foreground sm:block">
              Multi-agent wedding planning
            </span>
          </span>
        </Link>

        <nav className="flex items-center gap-1 text-sm" aria-label="Main">
          {NAV_LINKS.map((link) => {
            const active = link.match(pathname);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "rounded-full px-3 py-1.5 font-medium transition-colors",
                  active
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                )}
                aria-current={active ? "page" : undefined}
              >
                {link.label}
              </Link>
            );
          })}
          <span className="ml-1 flex items-center gap-1 pl-2">
            <RuntimeStatus health={health} loading={loading} offline={offline} />
            <button
              type="button"
              onClick={() => void refresh()}
              disabled={loading}
              className="rounded-full p-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground disabled:opacity-50"
              aria-label="Recheck backend status"
              title="Recheck backend status"
            >
              <RefreshCw className={cn("size-3.5", loading && "animate-spin")} aria-hidden />
            </button>
          </span>
        </nav>
      </div>
    </header>
  );
}
