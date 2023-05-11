class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'text', 'pub_date')
    search_fields = ('author', 'text')
    list_filter = ('author', 'pub_date')
    empty_value_diplay = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'review', 'text', 'pub_date')
    search_fields = ('author', 'review')
    list_filter = ('author', 'review', 'pub_date')
    empty_value_display = '-пусто-'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Comments, CommentAdmin)
admin.site.register(Review, ReviewAdmin)
