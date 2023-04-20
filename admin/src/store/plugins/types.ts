import { Plugins } from '@models/Plugins'
import { AsyncStateBase } from '@models/commons'

export interface PluginsState extends AsyncStateBase {
  plugins: Array<{ id: string, name: string, description: string }>
  data: Plugins
}