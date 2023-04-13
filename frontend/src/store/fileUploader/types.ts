import { type AsyncState } from '@models/commons'
import { type RabbitHoleServiceResponse } from '@services/RabbitHole'

/**
 * Defines the structure of the redux 'fileUploader' state.
 * This state contains information about the last file that the user has sent to the bot as well as the response form the server.
 * It extends the AsyncState interface, which defines the structure of the state of an asynchronous operation.
 */
export type FileUploaderState = AsyncState<RabbitHoleServiceResponse>
