import { api } from '@/shared/api/client'
import type { AuthUser, LoginResponse, LoginCredentials } from '../types'

/**
 * Payload for updating user profile information.
 */
export interface UpdateUserPayload {
    /** User's first name. */
    first_name?: string
    /** User's last name. */
    last_name?: string
}

/**
 * Payload for new user registration.
 */
export interface RegisterPayload {
    /** Unique email address for the account. */
    email: string
    /** Primary password. */
    password1: string
    /** Confirmation of the primary password. */
    password2: string
    /** User's legal first name. */
    first_name: string
    /** User's legal last name. */
    last_name: string
    /** Specified role for the account. */
    role: 'trainer' | 'client'
}

/**
 * API methods for authentication and user account management.
 */
export const authApi = {
    /**
     * Authenticates a user with the provided credentials.
     *
     * @param credentials The user's login email and password.
     * @return A promise resolving to the authenticated user's profile.
     */
    login: async (credentials: LoginCredentials): Promise<AuthUser> => {
        const response = await api.post<LoginResponse>('/auth/login/', credentials)
        return response.user
    },

    /**
     * Terminate the current user session.
     *
     * @return A promise resolving when the logout operation completes.
     */
    logout: () => api.post<void>('/auth/logout/'),

    /**
     * Retrieves the profile data for the currently authenticated user.
     *
     * @return A promise resolving to the AuthUser object.
     */
    getUser: () => api.get<AuthUser>('/auth/user/'),

    /**
     * Updates basic profile information for the current user.
     *
     * @param payload The fields to be updated.
     * @return A promise resolving to the updated user profile.
     */
    updateUser: (payload: UpdateUserPayload): Promise<AuthUser> =>
        api.patch<AuthUser>('/auth/user/', payload),

    /**
     * Uploads and updates the user's avatar image using multipart/form-data.
     *
     * @param file The image file to be uploaded.
     * @return A promise resolving to the updated user profile.
     */
    updateAvatar: (file: File): Promise<AuthUser> => {
        const form = new FormData()
        form.append('avatar', file)
        return api.patch<AuthUser>('/auth/user/', form, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
    },

    /**
     * Creates a new user account with the provided registration details.
     *
     * @param payload The registration data.
     * @return A promise resolving to the newly registered user's profile.
     */
    register: async (payload: RegisterPayload): Promise<AuthUser> => {
        const response = await api.post<LoginResponse>('/auth/registration/', payload)
        return response.user
    },

    /**
     * Sends a password reset request email.
     *
     * @param email The account email address.
     * @return A promise resolving when the request is sent.
     */
    forgotPassword: (email: string) => api.post<void>('/auth/password/reset/', { email }),

    /**
     * Finalizes the password reset process using tokens and new password values.
     *
     * @param payload The verification tokens and new password credentials.
     * @return A promise resolving when the password has been reset.
     */
    resetPasswordConfirm: (payload: {
        uid: string
        token: string
        new_password1: string
        new_password2: string
    }) => api.post<void>('/auth/password/reset/confirm/', payload),
}
