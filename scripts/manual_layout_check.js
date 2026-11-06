() => {
    // Shared by both manual builds and the translation editor preview. Keep it a single
    // expression returning [{page, message}] so both can evaluate it unchanged.
    const errors = [];
    const add = (page, message) => errors.push({page, message});
    for (const img of document.images)
        if (!img.complete || !img.naturalWidth) add(img.closest('.page')?.id || '', 'Missing image: ' + img.alt);
    for (const sheet of document.querySelectorAll('.page')) {
        const footer = sheet.querySelector('footer').getBoundingClientRect();
        for (const el of sheet.querySelectorAll('article, nav, .intro, .key-grid, .catalog-note, .dimension-notes, .paired-steps, .paired-step, .paired-images, .sff-reference-board, .sff-gallery-grid, .cover-copy')) {
            if (el.getBoundingClientRect().bottom > footer.top - 8) add(sheet.id, 'Footer collision: ' + sheet.id);
            for (const child of el.children)
                if (child.getBoundingClientRect().bottom > footer.top - 8) add(sheet.id, 'Content overflow: ' + sheet.id);
        }
        const contact = sheet.querySelector('.contact-block');
        if (contact)
            for (const el of sheet.querySelectorAll('article'))
                if (el.getBoundingClientRect().bottom > contact.getBoundingClientRect().top - 8) add(sheet.id, 'Contact block collision: ' + sheet.id);
        if (sheet.scrollWidth > sheet.clientWidth + 1 || sheet.scrollHeight > sheet.clientHeight + 1)
            add(sheet.id, 'Page overflow: ' + sheet.id);
    }
    for (const link of document.querySelectorAll('a[href^="#"]'))
        if (!document.getElementById(link.hash.slice(1))) add(link.closest('.page')?.id || '', 'Broken link: ' + link.hash);
    return errors;
}
