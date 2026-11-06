import { PlanDetail } from "@/components/plan-detail";

export default async function PlanDetailPage({ params }: PageProps<"/plans/[id]">) {
  const { id } = await params;
  return (
    <section className="mx-auto max-w-5xl px-4 pt-8 pb-12 sm:px-6">
      <PlanDetail planId={id} />
    </section>
  );
}
