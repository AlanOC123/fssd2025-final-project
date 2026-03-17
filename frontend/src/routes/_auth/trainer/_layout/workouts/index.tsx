import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_auth/trainer/_layout/workouts/')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/_auth/trainer/workouts/"!</div>
}
