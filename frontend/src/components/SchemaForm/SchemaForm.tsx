import React, { type FC, useCallback } from 'react'
import clsx from 'clsx'
import validator from '@rjsf/validator-ajv8'
import { type IChangeEvent } from '@rjsf/core'
import Form from '@rjsf/antd'
import { type JSONSchema } from '@models/JSONSchema'
import { type CommonProps } from '@models/commons'
import { type LLMSettings } from '@models/LLMSettings'

import style from './SchemaForm.module.scss'

/**
 * SchemaForm component description
 */
const SchemaForm: FC<SchemaFormProps> = ({ schema, onSubmit, className }) => {
  const classList = clsx(style.form, className)

  const handleChange = useCallback((data: IChangeEvent) => {
    if (onSubmit) {
      onSubmit(data.formData)
    }
  }, [onSubmit])

  return (
    <Form
      schema={schema}
      validator={validator}
      onSubmit={handleChange}
      className={classList}
    />
  )
}

export interface SchemaFormProps extends Omit<CommonProps, 'style'> {
  schema: JSONSchema
  data?: LLMSettings
  onSubmit?: (data: LLMSettings) => void
}

export default SchemaForm
