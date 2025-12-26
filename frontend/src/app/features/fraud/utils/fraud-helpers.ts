import { DecisionType } from '../enums/decision.enum';
import { HITLStatus } from '../enums/hitl-status.enum';
import { TransactionRandom } from '../interfaces/transaction-random.interface';

export class FraudHelpers {
  /**
   * Obtiene la severidad visual para una decisión de fraude.
   * @param decision Tipo de decisión
   * @returns Severidad: 'success' | 'warn' | 'danger' | 'info' | 'secondary'
   */
  static getDecisionSeverity(
    decision: string
  ): 'success' | 'warn' | 'danger' | 'info' | 'secondary' {
    switch (decision) {
      case DecisionType.APPROVE:
        return 'success';
      case DecisionType.CHALLENGE:
        return 'warn';
      case DecisionType.BLOCK:
        return 'danger';
      case DecisionType.ESCALATE_TO_HUMAN:
        return 'info';
      default:
        return 'secondary';
    }
  }

  /**
   * Obtiene la severidad visual según el estado de HITL.
   * @param status Estado del HITL
   * @returns Severidad: 'success' | 'warn' | 'danger' | 'info' | 'secondary'
   */
  static getStatusSeverity(
    status: string
  ): 'success' | 'warn' | 'danger' | 'info' | 'secondary' {
    switch (status) {
      case HITLStatus.APPROVED:
        return 'success';
      case HITLStatus.PENDING:
        return 'warn';
      case HITLStatus.REJECTED:
        return 'danger';
      case HITLStatus.IN_REVIEW:
        return 'info';
      default:
        return 'secondary';
    }
  }

  /**
   * Devuelve la clase CSS de fondo y borde según la decisión.
   * @param decision Tipo de decisión
   * @returns Clase CSS para estilo visual
   */
  static getResultClass(decision: string): string {
    switch (decision) {
      case DecisionType.APPROVE:
        return 'bg-green-100 border-green-500';
      case DecisionType.CHALLENGE:
        return 'bg-yellow-100 border-yellow-500';
      case DecisionType.BLOCK:
        return 'bg-red-100 border-red-500';
      case DecisionType.ESCALATE_TO_HUMAN:
        return 'bg-blue-100 border-blue-500';
      default:
        return 'bg-gray-100 border-gray-500';
    }
  }

  /**
   * Convierte un timestamp a formato ISO estándar.
   * @param timestamp Fecha en string
   * @returns Timestamp en formato ISO
   */
  static formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toISOString();
  }

  /**
   * Genera un timestamp aleatorio desde el inicio del año hasta la fecha actual.
   * @returns Date - objeto Date aleatorio de este año hasta hoy.
   */
  static generateRandomTimestamp(): Date {
    const now = new Date();
    const year = now.getFullYear();

    const start = new Date(year, 0, 1).getTime();
    const end = now.getTime();

    const randomTime = start + Math.random() * (end - start);

    return new Date(randomTime);
  }

  /**
   * Genera una transacción aleatoria con PESOS para simular comportamiento real
   * 70% transacciones normales (APPROVE)
   * 15% transacciones sospechosas (CHALLENGE)
   * 10% transacciones muy sospechosas (BLOCK)
   * 5% transacciones críticas (ESCALATE_TO_HUMAN)
   */
  static generateRandomData(): TransactionRandom {
    const customers = ['CU-001', 'CU-002', 'CU-003', 'CU-004', 'CU-005'];

    // Datos habituales por cliente (según customer_behavior.json)
    const customerDefaults: { [key: string]: any } = {
      'CU-001': {
        country: 'PE',
        device: 'D-01',
        avgAmount: 500,
        hours: [8, 20],
      },
      'CU-002': {
        country: 'PE',
        device: 'D-02',
        avgAmount: 600,
        hours: [9, 21],
      },
    };

    // Seleccionar cliente
    const randomCustomer =
      customers[Math.floor(Math.random() * customers.length)];
    const defaults = customerDefaults[randomCustomer];

    // Determinar tipo de transacción (con pesos)
    const rand = Math.random();
    let transactionType:
      | 'NORMAL'
      | 'SUSPICIOUS'
      | 'VERY_SUSPICIOUS'
      | 'CRITICAL';

    if (rand < 0.7) {
      transactionType = 'NORMAL'; // 70%
    } else if (rand < 0.85) {
      transactionType = 'SUSPICIOUS'; // 15%
    } else if (rand < 0.95) {
      transactionType = 'VERY_SUSPICIOUS'; // 10%
    } else {
      transactionType = 'CRITICAL'; // 5%
    }

    let country: string;
    let device: string;
    let amount: number;
    let timestamp: Date;
    let merchant: string;
    let channel: string;

    const now = new Date();

    switch (transactionType) {
      case 'NORMAL':
        // Transacción completamente normal → APPROVE
        country = defaults.country; // Mismo país
        device = defaults.device; // Mismo dispositivo
        amount = defaults.avgAmount * (0.8 + Math.random() * 0.4); // ±20% del promedio

        // Horario dentro del rango habitual
        const normalHour =
          defaults.hours[0] +
          Math.floor(Math.random() * (defaults.hours[1] - defaults.hours[0]));
        timestamp = new Date(now);
        timestamp.setHours(normalHour, Math.floor(Math.random() * 60), 0, 0);

        merchant = ['M-001', 'M-002'][Math.floor(Math.random() * 2)]; // Comercios conocidos
        channel = ['web', 'mobile'][Math.floor(Math.random() * 2)];
        break;

      case 'SUSPICIOUS':
        // Una anomalía leve → CHALLENGE
        country = defaults.country;
        device = defaults.device;

        const anomaly = Math.random();
        if (anomaly < 0.5) {
          // Monto alto (2-3x)
          amount = defaults.avgAmount * (2 + Math.random());
        } else {
          // Horario inusual
          amount = defaults.avgAmount * (0.9 + Math.random() * 0.3);
          const lateHour = Math.random() < 0.5 ? 3 : 23;
          timestamp = new Date(now);
          timestamp.setHours(lateHour, Math.floor(Math.random() * 60), 0, 0);
        }

        if (!timestamp!) {
          const normalHour =
            defaults.hours[0] +
            Math.floor(Math.random() * (defaults.hours[1] - defaults.hours[0]));
          timestamp = new Date(now);
          timestamp.setHours(normalHour, Math.floor(Math.random() * 60), 0, 0);
        }

        merchant = ['M-001', 'M-002', 'M-003'][Math.floor(Math.random() * 3)];
        channel = ['web', 'mobile', 'atm'][Math.floor(Math.random() * 3)];
        break;

      case 'VERY_SUSPICIOUS':
        // 2-3 anomalías → BLOCK
        const useDifferentCountry = Math.random() < 0.5;
        country = useDifferentCountry
          ? ['BR', 'CL'][Math.floor(Math.random() * 2)]
          : defaults.country;
        device = useDifferentCountry
          ? defaults.device
          : this.generateDeviceId();
        amount = defaults.avgAmount * (4 + Math.random() * 3); // 4-7x

        const suspiciousHour = [2, 3, 4][Math.floor(Math.random() * 3)];
        timestamp = new Date(now);
        timestamp.setHours(
          suspiciousHour,
          Math.floor(Math.random() * 60),
          0,
          0
        );

        merchant = ['M-003', 'M-999'][Math.floor(Math.random() * 2)];
        channel = ['web', 'atm'][Math.floor(Math.random() * 2)];
        break;

      case 'CRITICAL':
        // Todas las señales rojas → ESCALATE_TO_HUMAN
        country = ['BR', 'CL', 'CO', 'AR'][Math.floor(Math.random() * 4)]; // País diferente
        device = this.generateDeviceId(); // Dispositivo nuevo
        amount = defaults.avgAmount * (10 + Math.random() * 10); // 10-20x

        timestamp = new Date(now);
        timestamp.setHours(
          Math.floor(Math.random() * 6),
          Math.floor(Math.random() * 60),
          0,
          0
        ); // 00:00-06:00

        merchant = 'M-999'; // Comercio desconocido
        channel = ['web', 'atm'][Math.floor(Math.random() * 2)];
        break;
    }

    return {
      transaction_id: this.generateTransactionId(),
      customer_id: randomCustomer,
      amount: Math.round(amount * 100) / 100,
      currency: 'PEN',
      country: country,
      channel: channel,
      device_id: device,
      merchant_id: merchant,
      timestamp: timestamp,
    };
  }

  /**
   * Genera un ID de transacción único.
   * @returns {string} ID en formato "TX-XXXXXXXX"
   */
  static generateTransactionId(): string {
    return 'TX-' + Math.random().toString(36).substring(2, 10).toUpperCase();
  }

  /**
   * Genera un ID de dispositivo aleatorio.
   * @returns {string} ID en formato "DV-XXXXXX"
   */
  static generateDeviceId(): string {
    return 'DV-' + Math.random().toString(36).substring(2, 8).toUpperCase();
  }
}
