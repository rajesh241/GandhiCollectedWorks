import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { ArticleViewComponent } from "./article-view/article-view.component";
import { ArticleListComponent } from "./article-list/article-list.component";


const routes: Routes = [
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
