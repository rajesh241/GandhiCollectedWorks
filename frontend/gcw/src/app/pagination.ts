import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export class Page<T> {
  count: number;      // total number of items
  page_no: number;      // total number of items
  total_pages: number;      // total number of items
  next: string;       // URL of the next page
  previous: string;   // URL of the previous page
  results: Array<T>;  // items for the current page
}

export function queryPaginated<T>(http: HttpClient, baseUrl: string, urlOrFilter?: string | object): Observable<Page<T>> {
  let params = new HttpParams();
  let url = baseUrl;
  
  if (typeof urlOrFilter === 'string') {
    // we were given a page URL, use it
    url = urlOrFilter;
  } else if (typeof urlOrFilter === 'object') {
    // we were given filtering criteria, build the query string
    // isnum = /^\d+$/.test(val);
    Object.keys(urlOrFilter).sort().forEach(key => {
      const value = urlOrFilter[key];
      console.log(key+value);
      if ( (value !== null) && (/^\d+$/.test(value)) ) {
	console.log(key+value)
        params = params.set(key, value.toString());
      }
      else if ( (value != null) && (key === "user_role")){
        params = params.set(key, value.toString());
      }
      else if ( (value != null) && (key === "search")){
        params = params.set(key, value.toString());
      }
      else if ( (value != null) && (key === "ordering")){
        params = params.set(key, value.toString());
      }
    });
  }

  const token = localStorage.getItem("id_token");
  let headers = new HttpHeaders();
  headers = headers.set("Authorization", "Bearer " + token)
  console.log(headers);
  return http.get<Page<T>>(url, {
    params: params
  });
}

export function queryPaginatedLocations<T>(http: HttpClient, baseUrl: string, geoBounds: object,urlOrFilter?: string | object): Observable<Page<T>> {
  let params = new HttpParams();
  let url = baseUrl;

  if (typeof urlOrFilter === 'string') {
    // we were given a page URL, use it
    url = urlOrFilter;
  } else if (typeof urlOrFilter === 'object') {
    // we were given filtering criteria, build the query string
    Object.keys(urlOrFilter).sort().forEach(key => {
      const value = urlOrFilter[key];
      if (value !== null) {
        params = params.set(key, value.toString());
      }
    });
  }

  const token = localStorage.getItem("id_token");
  let headers = new HttpHeaders();
  console.log(headers);
  return http.get<Page<T>>(url, {
    params: params
  });
}
