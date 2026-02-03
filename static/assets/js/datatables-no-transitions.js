/**
 * DataTables - Configuración Global Sin Transiciones
 * Se aplica automáticamente a todas las tablas con clase .dataTable
 */

(function() {
    'use strict';
    
    // Configuración global de DataTables
    if (typeof $.fn.dataTable !== 'undefined') {
        
        // Establecer defaults globales
        $.extend(true, $.fn.dataTable.defaults, {
            "bAutoWidth": false,
            "bSortClasses": false,
            "bStateSave": false,
            "bProcessing": false,
            "sDom": "lfrtip",
            "language": {
                "url": "//cdn.datatables.net/plug-ins/1.13.7/i18n/es-CL.json"
            },
            "responsive": true,
            "pageLength": 10,
            "drawCallback": function() {
                // Forzar sin transiciones después de cada redibujado
                setTimeout(function() {
                    $('*').css({'transition': 'none', 'animation': 'none'});
                }, 0);
            }
        });
    }
    
    // Auto-inicializar tablas cuando el DOM esté listo
    $(document).ready(function() {
        
        // Forzar sin transiciones antes de inicializar
        $('*').css({'transition': 'none', 'animation': 'none'});
        
        // Buscar todas las tablas con id que termine en "Table"
        $('table[id$="Table"]').each(function() {
            const $table = $(this);
            
            // Si no está inicializada, inicializarla
            if (!$.fn.DataTable.isDataTable($table)) {
                try {
                    $table.DataTable();
                    console.log('✅ DataTable inicializado:', $table.attr('id'));
                } catch(err) {
                    console.warn('⚠️ Error inicializando tabla:', $table.attr('id'), err);
                }
            }
        });
        
        // Forzar sin transiciones después de inicializar
        setTimeout(function() {
            $('*').css({'transition': 'none', 'animation': 'none'});
        }, 100);
        
        setTimeout(function() {
            $('*').css({'transition': 'none', 'animation': 'none'});
        }, 300);
    });
    
    // Interceptar cualquier inicialización manual de DataTables
    if (typeof $.fn.dataTable !== 'undefined') {
        const originalDataTable = $.fn.dataTable.Api;
        
        $.fn.dataTable.Api.register('draw()', function() {
            const result = originalDataTable.prototype.draw.apply(this, arguments);
            
            // Forzar sin transiciones después de draw
            setTimeout(function() {
                $('*').css({'transition': 'none', 'animation': 'none'});
            }, 0);
            
            return result;
        });
    }
    
})();