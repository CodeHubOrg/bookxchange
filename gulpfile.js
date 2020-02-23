var gulp = require('gulp');
var watch = gulp.watch;
var bs = require('browser-sync').create(); // create a browser sync instance.
var sass = require('gulp-sass');

function style(cb) {
    return gulp.src("sass/*.scss")
        .pipe(sass())
        .on("error", sass.logError)
        .pipe(gulp.dest("static/bookx/css"))
        .pipe(bs.reload({stream: true}));
        cb();
}


function browsersync() {
    bs.init({
        proxy: "localhost:8000",
        open:false        
    })
}

function reload() {
    bs.reload();
}

function watcher() {
    browsersync();
    watch("sass/**/*.scss").on('change', function(path, stats){
        console.log(path);
        style(reload);
    })
    // alternative - but neither actually reloads
    // watch("sass/**/*.scss",
    //      {interval: 1000, usePolling: true},
    //      gulp.series(style, reload));
    watch(["**/*.html"], function() {
        bs.reload();
    });
}

exports.style = style;
exports.watch = watcher;

gulp.task('default', function(){ 
    watcher();
});