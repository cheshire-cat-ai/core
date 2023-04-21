import { type Plugin } from '@models/Plugin'
import { type AsyncStateBase } from '@models/commons'

export interface PluginsState extends AsyncStateBase {
  data: Plugin[]
}
