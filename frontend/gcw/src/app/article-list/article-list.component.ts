import { Component } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';

import { Observable, Subject } from 'rxjs';
import { map, debounceTime, merge, share, startWith, switchMap } from 'rxjs/operators';

import { Page } from '../pagination';
import { Article } from "../models/article";
import { ArticleService } from "../services/article.service";

@Component({
  selector: 'app-article-list',
  templateUrl: './article-list.component.html',
  styleUrls: ['./article-list.component.css']
})
export class ArticleListComponent  {
  filterForm: FormGroup;
  page: Observable<Page<Article>>;
  pageUrl = new Subject<string>();
  success: boolean = false;
  viewDetail:boolean=false;
  dataLoaded: Promise<boolean>;
  article:Article;
  articleContent:string;
  constructor(
    private articleService: ArticleService
  ) {
    this.filterForm = new FormGroup({

      limit : new FormControl(),
      ordering : new FormControl(),
      search: new FormControl()
    });
    this.page = this.filterForm.valueChanges.pipe(
      debounceTime(200),
      startWith(this.filterForm.value),
      merge(this.pageUrl),
      switchMap(urlOrFilter => this.articleService.list(urlOrFilter)),
      share()
    );
    this.dataLoaded = Promise.resolve(true);
  }

  onPageChanged(url: string) {
    this.pageUrl.next(url);
  }
  loadpage(){
    console.log("Load page is getting executed")
    this.page = this.filterForm.valueChanges.pipe(
      debounceTime(200),
      startWith(this.filterForm.value),
      merge(this.pageUrl),
      switchMap(urlOrFilter => this.articleService.list(urlOrFilter)),
      share()
    );
    this.dataLoaded = Promise.resolve(true);
  }
  viewArticle(article1){
	  console.log(article1);
	  this.article = article1;
          let content1 = this.article.content.replace(/\r\n/g, "<br />");
          let content2 = content1.replace(/\n\r/g, "<br />");
	  let content3 = content2.replace(/\n/g, "<br />");
          let content4 = content3.replace(/\r/g, "<br />");
          this.articleContent = content4;
	  this.viewDetail = true;

  }
}
