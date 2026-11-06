import type { Metadata } from "next";

import { PlansList } from "@/components/plans-list";

export const metadata: Metadata = {
  title: "Plan history",
  description: "Browse and manage previously generated wedding plans.",
};

export default function PlansPage() {
  return (
    <section className="mx-auto max-w-4xl px-4 pt-8 pb-12 sm:px-6">
      <PlansList />
    </section>
  );
}
