/**
 * A centralized mapping of application route paths.
 * Groups routes by domain (e.g., trainer, client) to provide a type-safe
 * reference for navigation throughout the application.
 */
export const ROUTES = {
    login: '/login',
    register: '/register',
    forgotPassword: '/forgot-password',
    resetPassword: '/reset-password',
    /** Routes specific to the trainer domain. */
    trainer: {
        dashboard: '/trainer/dashboard',
        clients: '/trainer/clients',
        programs: '/trainer/programs',
        workouts: '/trainer/workouts',
        analytics: '/trainer/analytics',
        profile: '/trainer/profile',
    },
    /** Routes specific to the client domain. */
    client: {
        dashboard: '/client/dashboard',
        workouts: '/client/workouts',
        findTrainer: '/client/find-trainer',
        profile: '/client/profile',
    },
} as const
