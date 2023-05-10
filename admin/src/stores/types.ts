import type { AsyncState, UpdatableState, AsyncStateBase } from '@models/commons'
import type { RabbitHoleServiceResponse } from '@services/RabbitHole'
import type { LLMProviderDescriptor, LLMProviderMetaData } from '@models/LLMProvider'
import type { Message } from '@models/Message'
import type { Plugin } from '@models/Plugin'
import type { Notification } from '@models/Notification'
import type { EmbedderDescriptor, EmbedderMetaData } from '@models/Embedder'
import type { JSONSettings } from '@models/JSONSchema'

/**
 * Defines the structure of the redux 'fileUploader' state.
 * This state contains information about the last file that the user has sent to the bot as well as the response form the server.
 * It extends the AsyncState interface, which defines the structure of the state of an asynchronous operation.
 */
export type FileUploaderState = AsyncState<RabbitHoleServiceResponse>

/**
 * Defines the structure of the redux 'llmProviders' state.
 * This state contains information about the available language models.
 */
export interface LLMProvidersState extends UpdatableState<LLMProviderDescriptor> {
    selected?: LLMProviderMetaData['languageModelName']
    settings: Record<string, JSONSettings>
}

/**
 * Defines the structure of the redux 'messages' state.
 * This state contains information about the messages sent by the user and the bot,
 * as well as a list of default messages that can be sent by the user.
 * It extends the AsyncStateBase interface, which defines the structure of the state of an asynchronous operation.
 */
export interface MessagesState extends AsyncStateBase {
    ready: boolean
    messages: Message[]
    defaultMessages: string[]
}

/**
 * Defines the structure of the redux 'messages' state.
 * This state contains information about the messages sent by the user and the bot,
 * as well as a list of default messages that can be sent by the user.
 * It extends the AsyncStateBase interface, which defines the structure of the state of an asynchronous operation.
 */
export interface NotificationsState {
    history: Notification[]
}

export interface PluginsState extends AsyncStateBase {
    data: Plugin[]
}

export interface EmbeddersState extends UpdatableState<EmbedderDescriptor> {
    selected?: EmbedderMetaData['languageEmbedderName']
    settings: Record<string, JSONSettings>
}