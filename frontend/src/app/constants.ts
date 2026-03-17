export const ROUTES = {
    login: '/login',
    trainer: {
        dashboard: '/trainer/dashboard',
        clients: '/trainer/clients',
        programs: '/trainer/programs',
        workouts: "/trainer/workouts",
        analytics: "/trainer/analytics"
    },
    client: {
        dashboard: '/client/dashboard',
        workouts: '/client/workouts'
    }
} as const
