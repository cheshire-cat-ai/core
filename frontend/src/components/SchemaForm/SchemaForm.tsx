import React, { type FC, useCallback } from 'react'
import clsx from 'clsx'
import { EmptyReactElement } from '@utils/commons'
import validator from '@rjsf/validator-ajv8'
import { type IChangeEvent } from '@rjsf/core'
import Form from '@rjsf/antd'
import { type JSONSchema } from '@models/JSONSchema'
import { type CommonProps } from '@models/commons'
import { type LLMSettings } from '@models/LLMSettings'

import style from './SchemaForm.module.scss'

const templates = {
  ButtonTemplates: { SubmitButton: EmptyReactElement }
}

/**
 * SchemaForm component description
 */
const SchemaForm: FC<SchemaFormProps> = ({ data, schema, onChange, className }) => {
  const classList = clsx(style.form, className)

  const handleChange = useCallback((data: IChangeEvent) => {
    if (onChange) {
      onChange(data.formData)
    }
  }, [onChange])

  return (
    <Form
      schema={schema}
      formData={data}
      validator={validator}
      onChange={handleChange}
      templates={templates}
      className={classList}
    />
  )
}

export interface SchemaFormProps extends Omit<CommonProps, 'style'> {
  schema: JSONSchema
  data?: LLMSettings
  onChange?: (data: LLMSettings) => void
}

export default SchemaForm
