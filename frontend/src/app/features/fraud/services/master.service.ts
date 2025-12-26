import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { environment } from '../../../../environments/environment';
import { Customer } from '../interfaces/customer.interface';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class MasterService {
  http = inject(HttpClient);

  /**
   * Obtiene la lista de clientes.
   */
  getCustomers() {
    return this.http
      .get<Customer[]>(`${environment.apiUrl}/api/v1/masters/customers`)
      .pipe(
        map((customers) =>
          customers.map((customer) => ({
            ...customer,
            fullName: `${customer.nombre} ${customer.apellido} (${customer.customer_id})`,
          }))
        )
      );
  }

  getCountries() {
    return this.http.get<any>(`${environment.apiUrl}/api/v1/masters/countries`);
  }

  getChannels() {
    return this.http.get<any>(`${environment.apiUrl}/api/v1/masters/channels`);
  }

  getMerchants() {
    return this.http.get<any>(`${environment.apiUrl}/api/v1/masters/merchants`);
  }
}
