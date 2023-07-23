const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');
const { PDFDocument, rgb } = require('pdf-lib');
const yargs = require('yargs');


// 封装命令行参数解析函数
function parseCommandLineArgs() {
  console.log("example: node convert_html_to_pdf.js -f '人类 某某 ISFJ' -n 10 -e '～/.cache/puppeteer/chrome/mac_arm-114.0.5735.133/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'")
  
  return yargs
  .option('f', {
    alias: 'file',
    describe: 'HTML 文件名',
    demandOption: true, // 是否必需
    type: 'string', // 参数类型
  })
  .option('n', {
    alias: 'numPages',
    describe: '页面数',
    demandOption: true,
    type: 'number',
  })
  .option('e', {
    alias: 'executablePath',
    describe: '指定 Chrome 可执行文件路径',
    demandOption: true,
    type: 'string',
  })
  .argv;
}

(async () => {
  try {
    // 定义计时器
    let startTime = new Date();
    let timer = setInterval(() => {
      let currentTime = new Date();
      let elapsedTime = currentTime - startTime;
      console.log(`已执行时间：${elapsedTime/1000}秒`);
    }, 1000); // 每隔1秒打印一次执行时间
    
    
    // 使用 yargs 定义命令行参数和选项参数
    const argv = parseCommandLineArgs();
    
    // 从 argv 对象中获取命令行参数和选项参数
    const htmlFileName = argv.file;
    const numPages = argv.numPages;
    const executablePath = argv.executablePath;
    
    console.log('HTML 文件名:', htmlFileName);
    console.log('页面数:', numPages);
    console.log('测试版的谷歌路径:', executablePath);
    
    // 启动 Puppeteer，使用已准备就绪的 Chrome 可执行文件，并设置超时时间为1200秒
    const browser = await puppeteer.launch({ executablePath, headless: true});

    // 创建一个新的页面
    const page = await browser.newPage();
    
    // 等待一段时间，确保页面中的内容加载完成,打开自己的 html，看至少多长时间能加载完毕，这里设置的时间要比较大一些 10 min
    await page.setDefaultNavigationTimeout(600000);
    console.log('page.setDefaultNavigationTimeout');

    // 指定待转换的 HTML 文件路径
    const htmlFilePath = path.join(__dirname, `${htmlFileName}.html`);

    // 使用 page.goto 打开页面，并等待 'domcontentloaded' 事件触发后执行后续操作，80s到了这里
    await page.goto('file://' + htmlFilePath, { waitUntil: 'domcontentloaded' });
    console.log('page.goto');

    // 获取滚动部分的实际高度要与分割的页数成正比，不然页与页之间的缝隙有影响，可根据实际pdf大小调节
    const scrollableHeight = await page.evaluate((numPages) => {
      const scrollableElement = document.querySelector('.chatScorll');
      // 这里加的值不能超过 1000？是什么 B 原因？
      return scrollableElement ? scrollableElement.scrollHeight + numPages * 25 : 0;
    }, numPages);

    // 获取滚动部分的实际宽度（假设滚动部分的宽度是固定的）
    const scrollableWidth = await page.evaluate(() => {
      const scrollableElement = document.querySelector('.chatScorll');
      return scrollableElement ? scrollableElement.scrollWidth : 800;
    });

    // 调整页面的视口大小，确保整个可滚动部分完整显示在 PDF 中
    await page.setViewport({ width: scrollableWidth, height: scrollableHeight});
    console.log('page.setViewport');

    // 将页面内容分页
    const pageHeight = scrollableHeight / numPages;
    
    // 创建一个 PDF 文件
    const pdfFilePath = path.join(__dirname, `${htmlFileName}.pdf`);
   
    // 获取滚动元素
    const scrollableElement = await page.$('.chatScorll');
    
    // 分页操作，设置每一页的高度
    await page.evaluate((element, pageHeight, numPages) => {
      element.style.height = `${numPages * pageHeight}px`;
    }, scrollableElement, pageHeight, numPages);
    console.log('page.evaluate');

    // 将当前页面导出为 PDF 20min
    const pdfOptions = {
      width: scrollableWidth,
      height: pageHeight,
      printBackground: true,
      preferCSSPageSize: true,
      timeout:1200000
    };
   
     try {
       const pdfBytes = await page.pdf(pdfOptions);
       // 处理转换后的PDF内容
       console.log('pdfBytes');
     
       // 将当前页的 PDF 保存到文件中
       fs.writeFileSync(pdfFilePath, pdfBytes);
       console.log('转换成功!');
     } catch (error) {
       console.error('PDF转换失败:', error);
     } finally {
       // 关闭浏览器
       await browser.close();
       console.log('browser.close');
     
       clearInterval(timer); // 清除计时器
       let endTime = new Date();
       let totalExecutionTime = endTime - startTime;
       console.log(`总执行时间: ${totalExecutionTime / 1000}秒`);
     }
     
  } catch (error) {
    console.error('转换出现错误：', error);
  }
})();
