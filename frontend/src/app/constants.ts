export const ROUTES = {
    login: '/login',
    register: '/register',
    forgotPassword: '/forgot-password',
    resetPassword: '/reset-password',
    trainer: {
        dashboard: '/trainer/dashboard',
        clients: '/trainer/clients',
        programs: '/trainer/programs',
        workouts: '/trainer/workouts',
        analytics: '/trainer/analytics',
        profile: '/trainer/profile',
    },
    client: {
        dashboard: '/client/dashboard',
        workouts: '/client/workouts',
        findTrainer: '/client/find-trainer',
        profile: '/client/profile',
    },
} as const
