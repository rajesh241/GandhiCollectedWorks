import { Component, OnInit, ViewChild, AfterViewInit } from '@angular/core';
import { Observable } from "rxjs";
import { Article } from "../models/article";
import { ArticleService } from "../services/article.service";
import { ActivatedRoute } from "@angular/router";

@Component({
  selector: 'app-article-view',
  templateUrl: './article-view.component.html',
  styleUrls: ['./article-view.component.css']
})
export class ArticleViewComponent implements OnInit {
  article : Observable<Article>;
  article_id: number;
  dataLoaded: Promise<boolean>;
  success: boolean=false; 
  errorMessage:string="";

  constructor(private articleService:ArticleService,
              private activatedRoute:ActivatedRoute) { }

  ngOnInit() {
    this.activatedRoute.paramMap.subscribe(
      params => {
         this.article_id=Number(params.get("id"));
      }  
    )
    this.loadArticleData();

  }
  loadArticleData(){
    this.articleService.getArticle(this.article_id)
         .subscribe(
            data => {
              this.article = data;
	      console.log(this.article);
              this.dataLoaded = Promise.resolve(true);
            }
          );
  }

}
