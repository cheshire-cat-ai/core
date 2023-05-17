/**
 * Defines the structure of a notification object.
 * A notification is a message that is displayed to the user.
 * It can be an error message, a success message, or a warning message.
 */
export interface Notification {
  readonly id: number
  readonly text: string
  readonly type?: 'info' | 'success' | 'error'
  hidden?: boolean
}
