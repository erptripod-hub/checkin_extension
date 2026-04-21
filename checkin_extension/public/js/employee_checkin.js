frappe.ui.form.on('Employee Checkin', {
    refresh: function(frm) {
        // Make GPS link clickable
        if (frm.doc.gps_link) {
            frm.fields_dict.gps_link.$wrapper.find('.like-disabled-input, .control-value').html(
                `<a href="${frm.doc.gps_link}" target="_blank" style="color: #2490EF; font-weight: 500;">
                    📍 Open in Google Maps
                </a>`
            );
        }
        
        // Show coordinates
        if (frm.doc.latitude && frm.doc.longitude) {
            frm.set_intro(`GPS: ${frm.doc.latitude.toFixed(6)}, ${frm.doc.longitude.toFixed(6)}`);
        }
    },
    
    onload: function(frm) {
        frm.set_query('project', function() {
            return {
                filters: { 'status': ['not in', ['Completed', 'Cancelled']] }
            };
        });
    }
});
