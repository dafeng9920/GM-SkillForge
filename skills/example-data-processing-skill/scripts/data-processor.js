/**
 * 示例数据处理器
 * 演示完整的skill实现，包含验证、转换、清洗功能
 */

class DataProcessingSkill {
  constructor(options = {}) {
    this.options = {
      maxFileSize: options.maxFileSize || 100 * 1024 * 1024, // 100MB
      timeout: options.timeout || 30000, // 30秒
      batchSize: options.batchSize || 1000,
      ...options
    };
    
    this.stats = {
      totalRecords: 0,
      processedRecords: 0,
      errorRecords: 0,
      startTime: null,
      endTime: null
    };
    
    this.errors = [];
  }

  /**
   * 主处理方法
   */
  async process(config) {
    this.stats.startTime = Date.now();
    
    try {
      // 1. 加载数据
      const rawData = await this.loadData(config.data_source, config.format);
      
      // 2. 验证数据
      const validationResults = this.validateData(rawData, config.validation_schema);
      
      // 3. 处理数据
      const processedData = await this.processData(rawData, config.processing_rules);
      
      // 4. 格式化输出
      const formattedData = this.formatOutput(processedData, config.output_format);
      
      this.stats.endTime = Date.now();
      
      return {
        processed_data: formattedData,
        processing_summary: {
          total_records: this.stats.totalRecords,
          processed_records: this.stats.processedRecords,
          error_records: this.stats.errorRecords,
          processing_time_ms: this.stats.endTime - this.stats.startTime
        },
        validation_results: validationResults,
        error_log: this.errors
      };
      
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  /**
   * 加载数据
   */
  async loadData(source, format) {
    console.log(`Loading data from ${source} in ${format} format...`);
    
    // 模拟数据加载
    const sampleData = [
      { id: 1, full_name: "  John Doe  ", email: "JOHN@EXAMPLE.COM", birth_year: 1990 },
      { id: 2, full_name: "Jane Smith", email: "jane@example.com", birth_year: 1985 },
      { id: 3, full_name: "", email: "invalid-email", birth_year: "not-a-year" }
    ];
    
    this.stats.totalRecords = sampleData.length;
    return sampleData;
  }

  /**
   * 验证数据
   */
  validateData(data, schema) {
    if (!schema) return [];
    
    const results = [];
    
    data.forEach((record, index) => {
      const recordErrors = [];
      
      // 检查必填字段
      if (schema.required) {
        schema.required.forEach(field => {
          if (!record[field] || record[field].toString().trim() === '') {
            recordErrors.push(`Missing required field: ${field}`);
          }
        });
      }
      
      // 检查数据类型
      if (schema.types) {
        Object.entries(schema.types).forEach(([field, expectedType]) => {
          if (record[field] !== undefined && typeof record[field] !== expectedType) {
            recordErrors.push(`Invalid type for field ${field}: expected ${expectedType}, got ${typeof record[field]}`);
          }
        });
      }
      
      results.push({
        record_index: index,
        record_id: record.id,
        valid: recordErrors.length === 0,
        errors: recordErrors
      });
      
      if (recordErrors.length > 0) {
        this.stats.errorRecords++;
        this.errors.push({
          type: 'validation_error',
          record_index: index,
          errors: recordErrors
        });
      }
    });
    
    return results;
  }

  /**
   * 处理数据
   */
  async processData(data, rules) {
    if (!rules || rules.length === 0) {
      this.stats.processedRecords = data.length;
      return data;
    }
    
    const processedData = [];
    
    for (const record of data) {
      try {
        let processedRecord = { ...record };
        
        // 应用处理规则
        for (const rule of rules) {
          processedRecord = this.applyRule(processedRecord, rule);
        }
        
        // 数据清洗
        processedRecord = this.cleanData(processedRecord);
        
        processedData.push(processedRecord);
        this.stats.processedRecords++;
        
      } catch (error) {
        this.handleRecordError(error, record);
      }
    }
    
    return processedData;
  }

  /**
   * 应用处理规则
   */
  applyRule(record, rule) {
    switch (rule.type) {
      case 'rename':
        if (record[rule.from] !== undefined) {
          record[rule.to] = record[rule.from];
          delete record[rule.from];
        }
        break;
        
      case 'format':
        if (record[rule.field] !== undefined) {
          record[rule.field] = this.formatValue(record[rule.field], rule.format);
        }
        break;
        
      case 'calculate':
        record[rule.field] = this.calculateValue(record, rule.expression);
        break;
        
      case 'clean':
        if (rule.fields) {
          rule.fields.forEach(field => {
            if (record[field] && typeof record[field] === 'string') {
              record[field] = record[field].trim();
            }
          });
        }
        break;
        
      default:
        console.warn(`Unknown rule type: ${rule.type}`);
    }
    
    return record;
  }

  /**
   * 格式化值
   */
  formatValue(value, format) {
    switch (format) {
      case 'lowercase':
        return value.toString().toLowerCase();
      case 'uppercase':
        return value.toString().toUpperCase();
      case 'trim':
        return value.toString().trim();
      case 'phone':
        return this.formatPhoneNumber(value);
      default:
        return value;
    }
  }

  /**
   * 计算值
   */
  calculateValue(record, expression) {
    // 简单的表达式计算示例
    if (expression === 'current_year - birth_year') {
      const currentYear = new Date().getFullYear();
      const birthYear = parseInt(record.birth_year);
      return isNaN(birthYear) ? null : currentYear - birthYear;
    }
    
    return null;
  }

  /**
   * 数据清洗
   */
  cleanData(record) {
    const cleaned = { ...record };
    
    // 清理字符串字段
    Object.keys(cleaned).forEach(key => {
      if (typeof cleaned[key] === 'string') {
        cleaned[key] = cleaned[key].trim();
      }
    });
    
    // 标准化邮箱
    if (cleaned.email) {
      cleaned.email = cleaned.email.toLowerCase();
      // 简单的邮箱验证
      if (!cleaned.email.includes('@') || !cleaned.email.includes('.')) {
        cleaned.email_valid = false;
      } else {
        cleaned.email_valid = true;
      }
    }
    
    return cleaned;
  }

  /**
   * 格式化电话号码
   */
  formatPhoneNumber(phone) {
    if (!phone) return phone;
    
    // 移除所有非数字字符
    const digits = phone.toString().replace(/\D/g, '');
    
    // 简单的美国电话号码格式化
    if (digits.length === 10) {
      return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
    }
    
    return phone;
  }

  /**
   * 格式化输出
   */
  formatOutput(data, format) {
    switch (format) {
      case 'json':
        return data;
      case 'csv':
        return this.convertToCSV(data);
      case 'xml':
        return this.convertToXML(data);
      default:
        return data;
    }
  }

  /**
   * 转换为CSV格式
   */
  convertToCSV(data) {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(',')];
    
    data.forEach(row => {
      const values = headers.map(header => {
        const value = row[header];
        return typeof value === 'string' ? `"${value}"` : value;
      });
      csvRows.push(values.join(','));
    });
    
    return csvRows.join('\n');
  }

  /**
   * 转换为XML格式
   */
  convertToXML(data) {
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<records>\n';
    
    data.forEach(record => {
      xml += '  <record>\n';
      Object.entries(record).forEach(([key, value]) => {
        xml += `    <${key}>${value}</${key}>\n`;
      });
      xml += '  </record>\n';
    });
    
    xml += '</records>';
    return xml;
  }

  /**
   * 处理记录错误
   */
  handleRecordError(error, record) {
    this.stats.errorRecords++;
    this.errors.push({
      type: 'processing_error',
      record_id: record.id,
      error: error.message,
      record: record
    });
    
    console.error(`Error processing record ${record.id}:`, error.message);
  }

  /**
   * 处理一般错误
   */
  handleError(error) {
    this.errors.push({
      type: 'system_error',
      error: error.message,
      stack: error.stack
    });
    
    console.error('System error:', error);
  }

  /**
   * 批量处理
   */
  async processBatch(configs) {
    const results = [];
    
    for (const config of configs) {
      try {
        const result = await this.process(config);
        results.push({
          config,
          result,
          success: true
        });
      } catch (error) {
        results.push({
          config,
          error: error.message,
          success: false
        });
      }
    }
    
    return results;
  }
}

// 导出类
if (typeof module !== 'undefined' && module.exports) {
  module.exports = DataProcessingSkill;
}

// 使用示例
if (require.main === module) {
  async function example() {
    const skill = new DataProcessingSkill();
    
    const result = await skill.process({
      data_source: './sample-data.json',
      format: 'json',
      processing_rules: [
        { type: 'rename', from: 'full_name', to: 'name' },
        { type: 'format', field: 'email', format: 'lowercase' },
        { type: 'calculate', field: 'age', expression: 'current_year - birth_year' },
        { type: 'clean', fields: ['name'] }
      ],
      output_format: 'json',
      validation_schema: {
        required: ['name', 'email'],
        types: {
          name: 'string',
          email: 'string',
          birth_year: 'number'
        }
      }
    });
    
    console.log('Processing Result:');
    console.log(JSON.stringify(result, null, 2));
  }
  
  example().catch(console.error);
}