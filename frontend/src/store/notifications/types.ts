import { type Notification } from '@models/Notification'

/**
 * Defines the structure of the redux 'messages' state.
 * This state contains information about the messages sent by the user and the bot,
 * as well as a list of default messages that can be sent by the user.
 * It extends the AsyncStateBase interface, which defines the structure of the state of an asynchronous operation.
 */
export interface NotificationsState {
  readonly history: Notification[]
}
