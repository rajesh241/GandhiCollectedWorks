import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { Article } from "../models/article";
import { environment } from '../../environments/environment';
import { Page, queryPaginated, queryPaginatedLocations} from '../pagination';


@Injectable({
  providedIn: 'root'
})
export class ArticleService {

  private endpoint = environment.apiURL+"/api/public/article/";
  constructor(private http :  HttpClient )  { }


  getArticle(id:number):Observable<any>{
    return this.http.get(this.endpoint+"?id="+id);
  }
  list(urlOrFilter?: string | object): Observable<Page<Article>> {
    return queryPaginated<Article>(this.http, this.endpoint, urlOrFilter);
  }
}
