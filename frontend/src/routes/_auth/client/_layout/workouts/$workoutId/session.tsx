import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute(
  '/_auth/client/_layout/workouts/$workoutId/session',
)({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/_auth/client/workouts/$workoutId/session"!</div>
}
